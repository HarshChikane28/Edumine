from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import require_role
from app.core.security import hash_password
from app.db.session import get_db
from app.models import Permission, TeacherPermission, TeacherProfile, User, UserRole
from app.schemas.admin import TeacherCreate, TeacherPermissionUpdate

router = APIRouter()

async def permission_rows(db: AsyncSession, keys: list[str]) -> list[Permission]:
    rows = list((await db.scalars(select(Permission).where(Permission.key.in_(keys)))).all())
    if len(rows) != len(set(keys)): raise HTTPException(status_code=400, detail="Unknown permission key")
    return rows

@router.post("/teachers")
async def create_teacher(payload: TeacherCreate, admin: User = Depends(require_role("admin")), db: AsyncSession = Depends(get_db)) -> dict:
    if await db.scalar(select(User).where(User.email == payload.email.lower())): raise HTTPException(409, "Email already exists")
    permissions = await permission_rows(db, payload.permissions)
    teacher = User(email=payload.email.lower(), password_hash=hash_password(payload.password), full_name=payload.full_name, role=UserRole.teacher, created_by=admin.id)
    db.add(teacher); await db.flush(); db.add(TeacherProfile(user_id=teacher.id))
    for permission in permissions: db.add(TeacherPermission(teacher_id=teacher.id, permission_id=permission.id, granted_by=admin.id))
    await db.commit()
    return {"id": str(teacher.id), "email": teacher.email, "role": teacher.role.value, "permissions": payload.permissions}

@router.get("/teachers")
async def list_teachers(_: User = Depends(require_role("admin")), db: AsyncSession = Depends(get_db)) -> list[dict]:
    teachers = list((await db.scalars(select(User).where(User.role == UserRole.teacher))).all()); response = []
    for teacher in teachers:
        keys = list((await db.scalars(select(Permission.key).join(TeacherPermission, TeacherPermission.permission_id == Permission.id).where(TeacherPermission.teacher_id == teacher.id))).all())
        response.append({"id": str(teacher.id), "email": teacher.email, "full_name": teacher.full_name, "is_active": teacher.is_active, "permissions": keys})
    return response

@router.patch("/teachers/{teacher_id}/permissions")
async def replace_permissions(teacher_id: UUID, payload: TeacherPermissionUpdate, admin: User = Depends(require_role("admin")), db: AsyncSession = Depends(get_db)) -> dict:
    teacher = await db.get(User, teacher_id)
    if not teacher or teacher.role != UserRole.teacher: raise HTTPException(404, "Teacher not found")
    permissions = await permission_rows(db, payload.permissions)
    await db.execute(delete(TeacherPermission).where(TeacherPermission.teacher_id == teacher_id))
    for permission in permissions: db.add(TeacherPermission(teacher_id=teacher_id, permission_id=permission.id, granted_by=admin.id))
    await db.commit(); return {"teacher_id": str(teacher_id), "permissions": payload.permissions}

@router.delete("/teachers/{teacher_id}")
async def deactivate_teacher(teacher_id: UUID, _: User = Depends(require_role("admin")), db: AsyncSession = Depends(get_db)) -> dict:
    teacher = await db.get(User, teacher_id)
    if not teacher or teacher.role != UserRole.teacher: raise HTTPException(404, "Teacher not found")
    teacher.is_active = False; await db.commit(); return {"deactivated": True}

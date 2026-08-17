from collections.abc import Callable
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_access_token
from app.core.config import settings
from app.db.session import get_db
from app.models import ClassRoom, Permission, StudentProfile, Subject, TeacherPermission, User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_current_user(token: str | None = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    if settings.auth_disabled and not token:
        user = await db.scalar(select(User).where(User.email == "admin@edusync.local"))
        if user and user.is_active:
            return user
        raise HTTPException(status_code=503, detail="Auth bypass is enabled but the seeded admin user is unavailable")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try: payload = decode_access_token(token); user_id = UUID(payload["sub"])
    except (ValueError, KeyError, TypeError): raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = await db.get(User, user_id)
    if not user or not user.is_active: raise HTTPException(status_code=401, detail="Inactive or missing user")
    return user

def require_role(*roles: str) -> Callable:
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role.value not in roles: raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return dependency

def require_permission(key: str) -> Callable:
    async def dependency(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> User:
        if user.role.value == "admin": return user
        if user.role.value != "teacher": raise HTTPException(status_code=403, detail="Insufficient role")
        query = select(TeacherPermission.id).join(Permission, Permission.id == TeacherPermission.permission_id).where(TeacherPermission.teacher_id == user.id, Permission.key == key)
        if not (await db.scalar(query)): raise HTTPException(status_code=403, detail=f"Missing permission: {key}")
        return user
    return dependency

async def assert_student_access(student_id: UUID, user: User, db: AsyncSession) -> None:
    if user.role != UserRole.student or user.id != student_id:
        if user.role == UserRole.admin: return
        if user.role == UserRole.teacher:
            profile = await db.get(StudentProfile, student_id)
            class_ids = await teacher_class_ids(db, user)
            if profile and class_ids and profile.class_id in class_ids: return
        if user.role not in (UserRole.admin, UserRole.teacher):
            raise HTTPException(status_code=403, detail="Students can only access their own records")
        raise HTTPException(status_code=403, detail="Teacher is outside this student's class scope")

async def teacher_subject_ids(db: AsyncSession, user: User) -> list[UUID] | None:
    if user.role == UserRole.admin: return None
    if user.role != UserRole.teacher: return []
    return list((await db.scalars(select(Subject.id).where(Subject.teacher_id == user.id))).all())

async def teacher_class_ids(db: AsyncSession, user: User) -> list[UUID] | None:
    if user.role == UserRole.admin: return None
    subject_ids = await teacher_subject_ids(db, user)
    if not subject_ids: return []
    return list((await db.scalars(select(Subject.class_id).where(Subject.id.in_(subject_ids)).distinct())).all())

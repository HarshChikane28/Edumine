from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import assert_student_access, get_current_user, require_permission
from app.core.security import hash_password
from app.db.session import get_db
from app.models import Assignment, AssignmentSubmission, ClassRoom, StudentProfile, User, UserRole
from app.schemas.admin import StudentCreate

router = APIRouter()

@router.post("/teachers/students")
async def create_student(payload: StudentCreate, teacher: User = Depends(require_permission("manage_students")), db: AsyncSession = Depends(get_db)) -> dict:
    if await db.scalar(select(User).where(User.email == payload.email.lower())): raise HTTPException(409, "Email already exists")
    profile_class = await db.get(ClassRoom, payload.class_id)
    if not profile_class: raise HTTPException(404, "Class not found")
    student = User(email=payload.email.lower(), password_hash=hash_password(payload.password), full_name=payload.full_name, role=UserRole.student, created_by=teacher.id)
    db.add(student); await db.flush(); db.add(StudentProfile(user_id=student.id, class_id=payload.class_id, roll_no=payload.roll_no, student_code=payload.student_code, created_by=teacher.id)); await db.commit()
    return {"id": str(student.id), "email": student.email, "role": student.role.value, "class_id": str(payload.class_id)}

@router.get("/teachers/students")
async def list_students(teacher: User = Depends(require_permission("manage_students")), db: AsyncSession = Depends(get_db)) -> list[dict]:
    profiles = list((await db.scalars(select(StudentProfile).where(StudentProfile.created_by == teacher.id))).all())
    if not profiles: return []
    users = {user.id: user for user in (await db.scalars(select(User).where(User.id.in_([profile.user_id for profile in profiles])))).all()}
    return [{"id": str(profile.user_id), "full_name": users[profile.user_id].full_name, "email": users[profile.user_id].email, "class_id": str(profile.class_id), "roll_no": profile.roll_no, "student_code": profile.student_code} for profile in profiles]

async def student_profile_or_404(student_id: UUID, user: User, db: AsyncSession) -> StudentProfile:
    await assert_student_access(student_id, user, db)
    profile = await db.get(StudentProfile, student_id)
    if not profile: raise HTTPException(404, "Student profile not found")
    return profile

@router.get("/{student_id}/dashboard")
async def dashboard(student_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    profile = await student_profile_or_404(student_id, user, db)
    assignments = await db.scalar(select(AssignmentSubmission).join(Assignment).where(Assignment.class_id == profile.class_id, AssignmentSubmission.student_id == student_id).limit(1))
    return {"student_id": str(student_id), "events": [], "announcement": None, "progress": [], "has_assignments": assignments is not None}

@router.get("/{student_id}/profile")
async def profile(student_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    profile = await student_profile_or_404(student_id, user, db); account = await db.get(User, student_id)
    return {"student_id": str(student_id), "name": account.full_name, "class_id": str(profile.class_id), "student_code": profile.student_code, "gpa": profile.gpa, "attendance": profile.attendance_pct}

@router.get("/{student_id}/insights")
async def insights(student_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    await student_profile_or_404(student_id, user, db)
    return {"student_id": str(student_id), "title": None, "text": None}

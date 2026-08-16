from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import require_permission
from app.core.security import hash_password
from app.db.session import get_db
from app.models import StudentProfile, User, UserRole
from app.schemas.admin import StudentCreate
router = APIRouter()

@router.post("/teachers/students")
async def create_student(payload: StudentCreate, teacher: User = Depends(require_permission("manage_students")), db: AsyncSession = Depends(get_db)) -> dict:
    if await db.scalar(select(User).where(User.email == payload.email.lower())): raise HTTPException(409, "Email already exists")
    student = User(email=payload.email.lower(), password_hash=hash_password(payload.password), full_name=payload.full_name, role=UserRole.student, created_by=teacher.id)
    db.add(student); await db.flush(); db.add(StudentProfile(user_id=student.id, class_id=payload.class_id, roll_no=payload.roll_no, student_code=payload.student_code, created_by=teacher.id)); await db.commit()
    return {"id": str(student.id), "email": student.email, "role": student.role.value, "class_id": str(payload.class_id)}

@router.get("/teachers/students")
async def list_students(teacher: User = Depends(require_permission("manage_students")), db: AsyncSession = Depends(get_db)) -> list[dict]:
    profiles = list((await db.scalars(select(StudentProfile).where(StudentProfile.created_by == teacher.id))).all())
    users = {user.id: user for user in (await db.scalars(select(User).where(User.id.in_([profile.user_id for profile in profiles])))).all()}
    return [{"id": str(profile.user_id), "full_name": users[profile.user_id].full_name, "email": users[profile.user_id].email, "class_id": str(profile.class_id), "roll_no": profile.roll_no, "student_code": profile.student_code} for profile in profiles]

@router.get("/{student_id}/dashboard")
async def dashboard(student_id: str) -> dict:
    return {"student_id": student_id, "events": [{"title": "Science Exhibition", "countdown": "20 Days Left"}, {"title": "Annual Function Day", "countdown": "5 Days Left"}], "announcement": {"title": "School Holiday", "body": "The campus will remain closed this Friday."}, "progress": [65, 78, 58, 86, 72, 92, 80]}

@router.get("/{student_id}/profile")
async def profile(student_id: str) -> dict:
    return {"student_id": student_id, "name": "Shashi Kant", "class_name": "Grade 12 • Section A", "student_code": "STU-2024-018", "gpa": 4.2, "attendance": 94, "assignments_completed": 12}

@router.get("/{student_id}/insights")
async def insights(student_id: str) -> dict:
    return {"student_id": student_id, "title": "You're building strong momentum", "text": "Your performance in science subjects has improved by 12% this term."}

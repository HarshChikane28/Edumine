from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import assert_student_access, get_current_user
from app.db.session import get_db
from app.models import Result, Subject, User

router = APIRouter()

@router.get("/{student_id}")
async def result(student_id: UUID, exam_id: UUID | None = None, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    await assert_student_access(student_id, user, db)
    query = select(Result, Subject).join(Subject, Subject.id == Result.subject_id).where(Result.student_id == student_id)
    if exam_id: query = query.where(Result.exam_id == exam_id)
    rows = (await db.execute(query)).all(); subjects = [{"subject": subject.name, "marks": result.marks, "grade": result.grade, "status": result.status.value} for result, subject in rows]
    average = sum(float(item["marks"]) for item in subjects) / len(subjects) if subjects else None
    return {"student_id": str(student_id), "exam_id": str(exam_id) if exam_id else None, "rank": None, "gpa": None, "average": average, "result": "Pending" if not subjects else "Passed", "subjects": subjects}

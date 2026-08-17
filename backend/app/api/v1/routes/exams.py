from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import require_permission, teacher_subject_ids
from app.db.session import get_db
from app.models import Exam, ExamSchedule, Subject, User

router = APIRouter()

@router.get("")
async def exams(user: User = Depends(require_permission("manage_exams")), db: AsyncSession = Depends(get_db)) -> dict:
    query = select(ExamSchedule, Exam, Subject).join(Exam, Exam.id == ExamSchedule.exam_id).join(Subject, Subject.id == ExamSchedule.subject_id)
    subject_ids = await teacher_subject_ids(db, user)
    if subject_ids is not None: query = query.where(ExamSchedule.subject_id.in_(subject_ids))
    rows = (await db.execute(query)).all()
    items = [{"id": str(schedule.id), "subject": subject.name, "date": schedule.date.isoformat(), "hall": schedule.hall, "status": schedule.status.value, "exam": exam.name} for schedule, exam, subject in rows]
    return {"summary": {"upcoming": len(items), "average_score": None, "grading_progress": None}, "items": items}

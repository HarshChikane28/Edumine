from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import assert_student_access, get_current_user
from app.db.session import get_db
from app.models import Assignment, AssignmentSubmission, StudentProfile, Subject, User

router = APIRouter()

@router.get("/{student_id}/assignments")
async def assignments(student_id: UUID, status: str | None = None, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    await assert_student_access(student_id, user, db)
    profile = await db.get(StudentProfile, student_id)
    if not profile: return {"student_id": str(student_id), "items": []}
    query = select(Assignment, AssignmentSubmission, Subject).join(Subject, Subject.id == Assignment.subject_id).outerjoin(AssignmentSubmission, (AssignmentSubmission.assignment_id == Assignment.id) & (AssignmentSubmission.student_id == student_id)).where(Assignment.class_id == profile.class_id)
    rows = (await db.execute(query)).all(); items = []
    for assignment, submission, subject in rows:
        current_status = submission.status.value if submission else "pending"
        if status and current_status.lower() != status.lower(): continue
        items.append({"id": str(assignment.id), "title": assignment.title, "subject": subject.name, "due": assignment.due_date.isoformat(), "status": current_status})
    return {"student_id": str(student_id), "items": items}

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user, require_permission, teacher_subject_ids
from app.db.session import get_db
from app.models import ClassRoom, StudentProfile, Subject, TimetableSlot, User, UserRole

router = APIRouter()

class TimetablePayload(BaseModel):
    grade: str
    section: str
    slots: list[dict]

@router.get("")
async def timetable(grade: str = "12", section: str = "A", user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    class_query = select(ClassRoom).where(ClassRoom.grade == grade, ClassRoom.section == section)
    if user.role == UserRole.student:
        profile = await db.get(StudentProfile, user.id)
        if not profile: raise HTTPException(404, "Student profile not found")
        class_query = select(ClassRoom).where(ClassRoom.id == profile.class_id)
    classroom = await db.scalar(class_query)
    if not classroom: raise HTTPException(404, "Class not found")
    query = select(TimetableSlot, Subject).join(Subject, Subject.id == TimetableSlot.subject_id).where(TimetableSlot.class_id == classroom.id)
    subject_ids = await teacher_subject_ids(db, user)
    if subject_ids is not None: query = query.where(TimetableSlot.subject_id.in_(subject_ids))
    rows = (await db.execute(query)).all()
    return {"grade": classroom.grade, "section": classroom.section, "slots": [{"id": str(slot.id), "day_of_week": slot.day_of_week, "period_number": slot.period_number, "subject": subject.name} for slot, subject in rows]}

@router.put("")
async def save_timetable(payload: TimetablePayload, user: User = Depends(require_permission("manage_timetable")), db: AsyncSession = Depends(get_db)) -> dict:
    classroom = await db.scalar(select(ClassRoom).where(ClassRoom.grade == payload.grade, ClassRoom.section == payload.section))
    if not classroom: raise HTTPException(404, "Class not found")
    subject_ids = await teacher_subject_ids(db, user)
    if subject_ids is not None:
        requested_ids = {UUID(item["subject_id"]) for item in payload.slots if item.get("subject_id")}
        if not requested_ids.issubset(set(subject_ids)): raise HTTPException(403, "Timetable contains a subject outside your scope")
    return {"saved": True, "grade": payload.grade, "section": payload.section, "slots": payload.slots}

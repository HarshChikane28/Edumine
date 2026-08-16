from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_permission, teacher_subject_ids
from app.db.session import get_db
from app.models import ClassRoom, StudentProfile, Subject, TimetableSlot, User, UserRole
from app.services.timetable import DAYS, PERIODS, PERIOD_BY_TIME, generate_recommendation


router = APIRouter()


class TimetableSlotPayload(BaseModel):
    day: str
    time: str
    subject_id: UUID | None = None


class TimetablePayload(BaseModel):
    grade: str
    section: str
    slots: list[TimetableSlotPayload] = Field(default_factory=list)


async def find_class(db: AsyncSession, grade: str, section: str) -> ClassRoom:
    grade_options = (grade, f"Grade {grade}" if not grade.lower().startswith("grade ") else grade.removeprefix("Grade "))
    classroom = await db.scalar(select(ClassRoom).where(ClassRoom.grade.in_(grade_options), ClassRoom.section == section))
    if not classroom:
        raise HTTPException(status_code=404, detail="Class not found")
    return classroom


async def classroom_for_user(db: AsyncSession, grade: str, section: str, user: User) -> ClassRoom:
    if user.role != UserRole.student:
        return await find_class(db, grade, section)
    profile = await db.get(StudentProfile, user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    classroom = await db.get(ClassRoom, profile.class_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Class not found")
    return classroom


async def serialize_timetable(db: AsyncSession, classroom: ClassRoom, slots: list[TimetableSlot], warnings: list[str] | None = None) -> dict:
    subjects = {subject.id: subject for subject in (await db.scalars(select(Subject).where(Subject.class_id == classroom.id))).all()}
    teacher_ids = {slot.teacher_id for slot in slots} | {subject.teacher_id for subject in subjects.values() if subject.teacher_id}
    teachers = {teacher.id: teacher for teacher in (await db.scalars(select(User).where(User.id.in_(teacher_ids)))).all()} if teacher_ids else {}
    labels = {number: label for number, label, _, _ in PERIODS}
    rows = []
    for slot in slots:
        subject = subjects.get(slot.subject_id)
        rows.append({"id": f"{DAYS[slot.day_of_week]}-{labels[slot.period_number]}", "day": DAYS[slot.day_of_week], "time": labels[slot.period_number], "subject": subject.name if subject else "Unknown subject", "subject_id": str(slot.subject_id), "teacher": teachers.get(slot.teacher_id).full_name if slot.teacher_id in teachers else "Unassigned"})
    rows.sort(key=lambda item: (item["time"], DAYS.index(item["day"])))
    return {"grade": classroom.grade.removeprefix("Grade "), "section": classroom.section, "slots": rows, "subjects": [{"id": str(subject.id), "name": subject.name, "teacher": teachers.get(subject.teacher_id).full_name if subject.teacher_id in teachers else "Unassigned", "weekly_periods": subject.weekly_periods} for subject in subjects.values()], "warnings": warnings or []}


def transient_slots(classroom: ClassRoom, recommendations: list) -> list[TimetableSlot]:
    period_details = {number: (starts, ends) for number, _, starts, ends in PERIODS}
    return [TimetableSlot(class_id=classroom.id, day_of_week=slot.day_of_week, period_number=slot.period_number, start_time=period_details[slot.period_number][0], end_time=period_details[slot.period_number][1], subject_id=slot.subject_id, teacher_id=slot.teacher_id) for slot in recommendations]


@router.get("/classes")
async def classes(_: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[dict]:
    rows = list((await db.scalars(select(ClassRoom).order_by(ClassRoom.grade.desc(), ClassRoom.section))).all())
    return [{"grade": classroom.grade.removeprefix("Grade "), "section": classroom.section} for classroom in rows]


@router.get("")
async def timetable(grade: str = "12", section: str = "A", user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    classroom = await classroom_for_user(db, grade, section, user)
    query = select(TimetableSlot).where(TimetableSlot.class_id == classroom.id)
    subject_ids = await teacher_subject_ids(db, user)
    if subject_ids is not None:
        query = query.where(TimetableSlot.subject_id.in_(subject_ids))
    slots = list((await db.scalars(query)).all())
    if slots:
        return await serialize_timetable(db, classroom, slots)
    recommendation, warnings = await generate_recommendation(db, classroom.id)
    if subject_ids is not None:
        recommendation = [slot for slot in recommendation if slot.subject_id in subject_ids]
    return await serialize_timetable(db, classroom, transient_slots(classroom, recommendation), warnings)


@router.post("/recommendation")
async def recommendation(grade: str = "12", section: str = "A", user: User = Depends(require_permission("manage_timetable")), db: AsyncSession = Depends(get_db)) -> dict:
    classroom = await find_class(db, grade, section)
    suggested, warnings = await generate_recommendation(db, classroom.id)
    subject_ids = await teacher_subject_ids(db, user)
    if subject_ids is not None:
        suggested = [slot for slot in suggested if slot.subject_id in subject_ids]
    return await serialize_timetable(db, classroom, transient_slots(classroom, suggested), warnings)


@router.put("")
async def save_timetable(payload: TimetablePayload, user: User = Depends(require_permission("manage_timetable")), db: AsyncSession = Depends(get_db)) -> dict:
    classroom = await find_class(db, payload.grade, payload.section)
    subjects = {subject.id: subject for subject in (await db.scalars(select(Subject).where(Subject.class_id == classroom.id))).all()}
    subject_ids = await teacher_subject_ids(db, user)
    requested_ids = {slot.subject_id for slot in payload.slots if slot.subject_id}
    if subject_ids is not None and not requested_ids.issubset(set(subject_ids)):
        raise HTTPException(status_code=403, detail="Timetable contains a subject outside your scope")

    # Admins replace a complete class timetable. Teachers replace only the
    # subject slots assigned to them, preserving the rest of the class plan.
    if subject_ids is None:
        await db.execute(delete(TimetableSlot).where(TimetableSlot.class_id == classroom.id))
    else:
        await db.execute(delete(TimetableSlot).where(TimetableSlot.class_id == classroom.id, TimetableSlot.subject_id.in_(subject_ids)))
    await db.flush()

    seen_slots: set[tuple[str, str]] = set()
    seen_teacher_slots: set[tuple[UUID, int, int]] = set()
    prepared: list[TimetableSlot] = []
    for slot in payload.slots:
        if not slot.subject_id:
            continue
        if slot.day not in DAYS or slot.time not in PERIOD_BY_TIME:
            raise HTTPException(status_code=422, detail="Invalid timetable day or time")
        if (slot.day, slot.time) in seen_slots:
            raise HTTPException(status_code=422, detail="A class slot was submitted twice")
        subject = subjects.get(slot.subject_id)
        if not subject or not subject.teacher_id:
            raise HTTPException(status_code=422, detail="Each slot needs a subject assigned to this class and teacher")
        day_of_week = DAYS.index(slot.day)
        period_number, start_time, end_time = PERIOD_BY_TIME[slot.time]
        teacher_key = (subject.teacher_id, day_of_week, period_number)
        if teacher_key in seen_teacher_slots:
            raise HTTPException(status_code=409, detail=f"Teacher conflict for {subject.name}")
        class_conflict = await db.scalar(select(TimetableSlot.id).where(TimetableSlot.class_id == classroom.id, TimetableSlot.day_of_week == day_of_week, TimetableSlot.period_number == period_number))
        teacher_conflict = await db.scalar(select(TimetableSlot.id).where(TimetableSlot.class_id != classroom.id, TimetableSlot.teacher_id == subject.teacher_id, TimetableSlot.day_of_week == day_of_week, TimetableSlot.period_number == period_number))
        if class_conflict or teacher_conflict:
            raise HTTPException(status_code=409, detail=f"Conflict for {subject.name} at {slot.day} {slot.time}")
        seen_slots.add((slot.day, slot.time)); seen_teacher_slots.add(teacher_key)
        prepared.append(TimetableSlot(class_id=classroom.id, day_of_week=day_of_week, period_number=period_number, start_time=start_time, end_time=end_time, subject_id=subject.id, teacher_id=subject.teacher_id))
    db.add_all(prepared)
    await db.commit()
    visible_slots = prepared if subject_ids is not None else list((await db.scalars(select(TimetableSlot).where(TimetableSlot.class_id == classroom.id))).all())
    return {"saved": True, **(await serialize_timetable(db, classroom, visible_slots))}

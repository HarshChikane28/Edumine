from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import ClassRoom, Subject, TimetableSlot, User, UserRole
from app.services.notifications import create_timetable_notification
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

class ClassPayload(BaseModel):
    grade: str = Field(min_length=1, max_length=40)
    section: str = Field(min_length=1, max_length=20)

class SubjectPayload(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    teacher_id: UUID
    weekly_periods: int = Field(ge=1, le=20)


async def find_class(db: AsyncSession, grade: str, section: str) -> ClassRoom:
    grade_options = (grade, f"Grade {grade}" if not grade.lower().startswith("grade ") else grade.removeprefix("Grade "))
    classroom = await db.scalar(select(ClassRoom).where(ClassRoom.grade.in_(grade_options), ClassRoom.section == section))
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
async def classes(db: AsyncSession = Depends(get_db)) -> list[dict]:
    rows = list((await db.scalars(select(ClassRoom).order_by(ClassRoom.grade.desc(), ClassRoom.section))).all())
    return [{"id": str(classroom.id), "grade": classroom.grade.removeprefix("Grade "), "section": classroom.section} for classroom in rows]

@router.get("/teachers")
async def teachers(db: AsyncSession = Depends(get_db)) -> list[dict]:
    rows = list((await db.scalars(select(User).where(User.role == UserRole.teacher, User.is_active.is_(True)).order_by(User.full_name))).all())
    return [{"id": str(teacher.id), "name": teacher.full_name, "email": teacher.email} for teacher in rows]

@router.post("/classes")
async def create_class(payload: ClassPayload, db: AsyncSession = Depends(get_db)) -> dict:
    grade = payload.grade.strip(); section = payload.section.strip().upper()
    if await db.scalar(select(ClassRoom).where(ClassRoom.grade == grade, ClassRoom.section == section)):
        raise HTTPException(status_code=409, detail=f"{grade} • Section {section} already exists")
    classroom = ClassRoom(grade=grade, section=section); db.add(classroom); await db.commit()
    return {"id": str(classroom.id), "grade": classroom.grade.removeprefix("Grade "), "section": classroom.section}

@router.delete("/classes/{class_id}")
async def delete_class(class_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    classroom = await db.get(ClassRoom, class_id)
    if not classroom: raise HTTPException(status_code=404, detail="Class not found")
    if await db.scalar(select(Subject.id).where(Subject.class_id == class_id)):
        raise HTTPException(status_code=409, detail="Remove this class's subjects before deleting the grade/section")
    db.delete(classroom); await db.commit(); return {"deleted": True}

@router.get("/configuration")
async def configuration(grade: str, section: str, db: AsyncSession = Depends(get_db)) -> dict:
    classroom = await find_class(db, grade, section)
    subjects = list((await db.scalars(select(Subject).where(Subject.class_id == classroom.id).order_by(Subject.name))).all())
    teacher_ids = {subject.teacher_id for subject in subjects if subject.teacher_id}
    teachers_by_id = {teacher.id: teacher for teacher in (await db.scalars(select(User).where(User.id.in_(teacher_ids)))).all()} if teacher_ids else {}
    return {"class_id": str(classroom.id), "grade": classroom.grade.removeprefix("Grade "), "section": classroom.section, "subjects": [{"id": str(subject.id), "name": subject.name, "teacher_id": str(subject.teacher_id), "teacher": teachers_by_id[subject.teacher_id].full_name, "weekly_periods": subject.weekly_periods} for subject in subjects]}

@router.post("/configuration/subjects")
async def create_subject(grade: str, section: str, payload: SubjectPayload, db: AsyncSession = Depends(get_db)) -> dict:
    classroom = await find_class(db, grade, section)
    teacher = await db.get(User, payload.teacher_id)
    if not teacher or teacher.role != UserRole.teacher or not teacher.is_active: raise HTTPException(status_code=422, detail="Select an active teacher")
    if await db.scalar(select(Subject).where(Subject.class_id == classroom.id, Subject.name == payload.name.strip())): raise HTTPException(status_code=409, detail="This subject already exists for the selected class")
    subject = Subject(name=payload.name.strip(), class_id=classroom.id, teacher_id=teacher.id, weekly_periods=payload.weekly_periods); db.add(subject); await db.commit()
    return {"id": str(subject.id), "name": subject.name, "teacher_id": str(teacher.id), "teacher": teacher.full_name, "weekly_periods": subject.weekly_periods}

@router.delete("/configuration/subjects/{subject_id}")
async def delete_subject(subject_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    subject = await db.get(Subject, subject_id)
    if not subject: raise HTTPException(status_code=404, detail="Subject not found")
    removed_slots = await db.execute(delete(TimetableSlot).where(TimetableSlot.subject_id == subject_id))
    await db.delete(subject); await db.commit()
    return {"deleted": True, "removed_timetable_slots": removed_slots.rowcount}


@router.get("")
async def timetable(grade: str = "12", section: str = "A", db: AsyncSession = Depends(get_db)) -> dict:
    classroom = await find_class(db, grade, section)
    query = select(TimetableSlot).where(TimetableSlot.class_id == classroom.id)
    slots = list((await db.scalars(query)).all())
    if slots:
        return await serialize_timetable(db, classroom, slots)
    recommendation, warnings = await generate_recommendation(db, classroom.id)
    return await serialize_timetable(db, classroom, transient_slots(classroom, recommendation), warnings)


@router.post("/recommendation")
async def recommendation(grade: str = "12", section: str = "A", db: AsyncSession = Depends(get_db)) -> dict:
    classroom = await find_class(db, grade, section)
    suggested, warnings = await generate_recommendation(db, classroom.id)
    return await serialize_timetable(db, classroom, transient_slots(classroom, suggested), warnings)


@router.put("")
async def save_timetable(payload: TimetablePayload, db: AsyncSession = Depends(get_db)) -> dict:
    classroom = await find_class(db, payload.grade, payload.section)
    subjects = {subject.id: subject for subject in (await db.scalars(select(Subject).where(Subject.class_id == classroom.id))).all()}
    await db.execute(delete(TimetableSlot).where(TimetableSlot.class_id == classroom.id))
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
        if class_conflict:
            raise HTTPException(status_code=409, detail=f"Class conflict: Grade {classroom.grade.removeprefix('Grade ')} • Section {classroom.section} already has a lesson at {slot.day} {slot.time}.")
        if teacher_conflict:
            raise HTTPException(status_code=409, detail=f"Teacher conflict: {subject.name}'s teacher is already teaching another class at {slot.day} {slot.time}.")
        seen_slots.add((slot.day, slot.time)); seen_teacher_slots.add(teacher_key)
        prepared.append(TimetableSlot(class_id=classroom.id, day_of_week=day_of_week, period_number=period_number, start_time=start_time, end_time=end_time, subject_id=subject.id, teacher_id=subject.teacher_id))
    db.add_all(prepared)
    await db.commit()
    create_timetable_notification(payload.grade, payload.section)
    saved_slots = list((await db.scalars(select(TimetableSlot).where(TimetableSlot.class_id == classroom.id))).all())
    return {"saved": True, **(await serialize_timetable(db, classroom, saved_slots))}

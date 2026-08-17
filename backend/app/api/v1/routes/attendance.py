from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import AttendanceRecord, AttendanceStatus, ClassRoom, RFIDCard, StudentProfile, User, UserRole

router = APIRouter()


class NFCScanPayload(BaseModel):
    card_uid: str = Field(min_length=2, max_length=120)
    device_label: str | None = Field(default=None, max_length=120)


def iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


async def student_rows(db: AsyncSession, student_code: str | None = None, grade: str | None = None, section: str | None = None) -> list[tuple[StudentProfile, User, ClassRoom]]:
    query = select(StudentProfile, User, ClassRoom).join(User, User.id == StudentProfile.user_id).join(ClassRoom, ClassRoom.id == StudentProfile.class_id).where(User.role == UserRole.student)
    if student_code:
        query = query.where(StudentProfile.student_code == student_code)
    if grade:
        grade_options = [grade, f"Grade {grade}"] if not grade.lower().startswith("grade") else [grade, grade.replace("Grade ", "")]
        query = query.where(ClassRoom.grade.in_(grade_options))
    if section:
        query = query.where(ClassRoom.section == section)
    return list((await db.execute(query.order_by(ClassRoom.grade.desc(), ClassRoom.section, StudentProfile.roll_no))).all())


async def serialize_student_attendance(db: AsyncSession, profile: StudentProfile, account: User, classroom: ClassRoom) -> dict:
    records = list((await db.scalars(select(AttendanceRecord).where(AttendanceRecord.student_id == profile.user_id).order_by(AttendanceRecord.attendance_date.desc(), AttendanceRecord.scanned_at.desc()))).all())
    present = sum(1 for record in records if record.status == AttendanceStatus.present)
    late = sum(1 for record in records if record.status == AttendanceStatus.late)
    total = len(records)
    percentage = round(((present + late) / total) * 100, 2) if total else float(profile.attendance_pct or 0)
    latest = records[0] if records else None
    today_record = next((record for record in records if record.attendance_date == date.today()), None)
    return {
        "student_id": str(profile.user_id),
        "student_name": account.full_name,
        "student_code": profile.student_code,
        "roll_no": profile.roll_no,
        "grade": classroom.grade,
        "section": classroom.section,
        "attendance_percentage": percentage,
        "present_days": present,
        "late_days": late,
        "recorded_days": total,
        "today_status": today_record.status.value if today_record else "not_marked",
        "latest_scan_at": iso(latest.scanned_at) if latest else None,
        "records": [
            {
                "id": str(record.id),
                "date": record.attendance_date.isoformat(),
                "status": record.status.value,
                "source": record.source,
                "scan_uid": record.scan_uid,
                "scanned_at": iso(record.scanned_at),
                "notes": record.notes,
            }
            for record in records[:30]
        ],
    }


@router.post("/scan")
async def record_nfc_scan(payload: NFCScanPayload, db: AsyncSession = Depends(get_db)) -> dict:
    card = await db.scalar(select(RFIDCard).where(RFIDCard.uid == payload.card_uid.strip(), RFIDCard.is_active.is_(True)))
    if not card:
        raise HTTPException(status_code=404, detail="NFC card is not linked to any active student")
    profile = await db.get(StudentProfile, card.student_id)
    account = await db.get(User, card.student_id)
    classroom = await db.get(ClassRoom, profile.class_id) if profile else None
    if not profile or not account or not classroom:
        raise HTTPException(status_code=404, detail="Student profile for this NFC card is missing")

    today = date.today()
    scanned_at = datetime.now(timezone.utc)
    record = await db.scalar(select(AttendanceRecord).where(AttendanceRecord.student_id == card.student_id, AttendanceRecord.attendance_date == today))
    created = record is None
    if record:
        record.status = AttendanceStatus.present
        record.source = "nfc"
        record.scan_uid = card.uid
        record.scanned_at = scanned_at
        record.notes = f"Updated by {payload.device_label}" if payload.device_label else "Updated by NFC scan"
    else:
        record = AttendanceRecord(student_id=card.student_id, class_id=profile.class_id, attendance_date=today, status=AttendanceStatus.present, source="nfc", scan_uid=card.uid, scanned_at=scanned_at, notes=f"Recorded by {payload.device_label}" if payload.device_label else "Recorded by NFC scan")
        db.add(record)

    records_count = await db.scalar(select(AttendanceRecord.id).where(AttendanceRecord.student_id == card.student_id).limit(1))
    if not records_count:
        profile.attendance_pct = Decimal("100.00")
    else:
        all_records = list((await db.scalars(select(AttendanceRecord).where(AttendanceRecord.student_id == card.student_id))).all())
        marked = sum(1 for item in all_records if item.status in (AttendanceStatus.present, AttendanceStatus.late))
        profile.attendance_pct = Decimal(str(round((marked / len(all_records)) * 100, 2))) if all_records else Decimal("100.00")

    await db.commit()
    await db.refresh(record)
    return {"recorded": True, "created": created, "message": "Attendance recorded", "attendance": await serialize_student_attendance(db, profile, account, classroom)}


@router.get("/overview")
async def attendance_overview(student_code: str = "STU-DEMO-001", db: AsyncSession = Depends(get_db)) -> dict:
    rows = await student_rows(db, student_code=student_code)
    if not rows:
        raise HTTPException(status_code=404, detail="Student not found")
    profile, account, classroom = rows[0]
    return await serialize_student_attendance(db, profile, account, classroom)


@router.get("/records")
async def attendance_records(grade: str | None = None, section: str | None = None, db: AsyncSession = Depends(get_db)) -> list[dict]:
    return [await serialize_student_attendance(db, profile, account, classroom) for profile, account, classroom in await student_rows(db, grade=grade, section=section)]


@router.get("/cards")
async def attendance_cards(db: AsyncSession = Depends(get_db)) -> list[dict]:
    rows = await db.execute(select(RFIDCard, StudentProfile, User, ClassRoom).join(StudentProfile, StudentProfile.user_id == RFIDCard.student_id).join(User, User.id == RFIDCard.student_id).join(ClassRoom, ClassRoom.id == StudentProfile.class_id).order_by(User.full_name))
    return [{"uid": card.uid, "label": card.label, "student_name": user.full_name, "student_code": profile.student_code, "grade": classroom.grade, "section": classroom.section, "active": card.is_active} for card, profile, user, classroom in rows.all()]

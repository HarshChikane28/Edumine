import asyncio
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import select
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import AttendanceRecord, AttendanceStatus, ClassRoom, Permission, RFIDCard, StudentProfile, Subject, TeacherPermission, TeacherProfile, TimetableSlot, User, UserRole
from app.services.timetable import PERIODS, generate_recommendation

PERMISSIONS = {"manage_students": "Create and edit student accounts and profiles", "manage_exams": "Create and edit exams and schedules", "enter_results": "Enter and edit student marks", "manage_timetable": "Create and edit timetable slots", "manage_assignments": "Create assignments and grade submissions", "manage_documents": "Approve and process document requests", "manage_activities": "Create and manage clubs and activities"}
TIMETABLE_TEACHERS = {
    "Mathematics": ("Ms. Priya Shah", "priya.shah@edusync.local"),
    "Physics": ("Mr. Arjun Mehta", "arjun.mehta@edusync.local"),
    "Chemistry": ("Dr. Neha Iyer", "neha.iyer@edusync.local"),
    "English": ("Mrs. Kavita Rao", "kavita.rao@edusync.local"),
    "Computer Lab": ("Mr. Rohan Das", "rohan.das@edusync.local"),
    "Physical Education": ("Coach Aman Verma", "aman.verma@edusync.local"),
}
SUBJECT_WORKLOADS = {"Mathematics": 4, "Physics": 4, "Chemistry": 4, "English": 3, "Computer Lab": 3, "Physical Education": 2}
DEMO_ATTENDANCE_STUDENTS = [
    ("Demo Student", "student@edusync.local", "STU-DEMO-001", "1", "Grade 12", "A", "DEMO-NFC-001"),
    ("Aarav Sharma", "aarav.sharma@edusync.local", "STU-DEMO-002", "2", "Grade 12", "A", "DEMO-NFC-002"),
    ("Isha Patel", "isha.patel@edusync.local", "STU-DEMO-003", "3", "Grade 12", "A", "DEMO-NFC-003"),
    ("Kabir Khan", "kabir.khan@edusync.local", "STU-DEMO-004", "4", "Grade 11", "A", "DEMO-NFC-004"),
    ("Meera Nair", "meera.nair@edusync.local", "STU-DEMO-005", "5", "Grade 10", "B", "DEMO-NFC-005"),
    ("Vihaan Joshi", "vihaan.joshi@edusync.local", "STU-DEMO-006", "6", "Grade 9", "A", "DEMO-NFC-006"),
    ("Anaya Deshmukh", "anaya.deshmukh@edusync.local", "STU-DEMO-007", "7", "Grade 8", "B", "DEMO-NFC-007"),
    ("Reyansh Kulkarni", "reyansh.kulkarni@edusync.local", "STU-DEMO-008", "8", "Grade 12", "A", "DEMO-NFC-008"),
    ("Saanvi More", "saanvi.more@edusync.local", "STU-DEMO-009", "9", "Grade 11", "A", "DEMO-NFC-009"),
    ("Advait Patil", "advait.patil@edusync.local", "STU-DEMO-010", "10", "Grade 10", "B", "DEMO-NFC-010"),
]
DEMO_ATTENDANCE_PATTERN = [
    (6, AttendanceStatus.present),
    (5, AttendanceStatus.late),
    (4, AttendanceStatus.present),
    (3, AttendanceStatus.absent),
    (2, AttendanceStatus.present),
    (1, AttendanceStatus.present),
]

async def seed() -> None:
    async with SessionLocal() as db:
        admin = await db.scalar(select(User).where(User.email == "admin@edusync.local"))
        if not admin:
            admin = User(email="admin@edusync.local", password_hash=hash_password("Admin@123"), full_name="EduSync Administrator", role=UserRole.admin)
            db.add(admin); await db.flush()
        for key, description in PERMISSIONS.items():
            if not await db.scalar(select(Permission).where(Permission.key == key)): db.add(Permission(key=key, description=description))
        for grade, section in [("Grade 12", "A"), ("Grade 11", "A"), ("Grade 10", "B"), ("Grade 9", "A"), ("Grade 8", "B")]:
            if not await db.scalar(select(ClassRoom).where(ClassRoom.grade == grade, ClassRoom.section == section)): db.add(ClassRoom(grade=grade, section=section))
        await db.flush()
        teachers: dict[str, User] = {}
        for subject_name, (full_name, email) in TIMETABLE_TEACHERS.items():
            teacher = await db.scalar(select(User).where(User.email == email))
            if not teacher:
                teacher = User(email=email, password_hash=hash_password("Teacher@123"), full_name=full_name, role=UserRole.teacher)
                db.add(teacher)
                await db.flush()
            if not await db.get(TeacherProfile, teacher.id): db.add(TeacherProfile(user_id=teacher.id))
            teachers[subject_name] = teacher
        classrooms = list((await db.scalars(select(ClassRoom))).all())
        for classroom in classrooms:
            for subject_name, weekly_periods in SUBJECT_WORKLOADS.items():
                if not await db.scalar(select(Subject).where(Subject.class_id == classroom.id, Subject.name == subject_name)):
                    db.add(Subject(name=subject_name, class_id=classroom.id, teacher_id=teachers[subject_name].id, weekly_periods=weekly_periods))
        await db.flush()
        period_details = {number: (starts, ends) for number, _, starts, ends in PERIODS}
        for classroom in classrooms:
            if await db.scalar(select(TimetableSlot.id).where(TimetableSlot.class_id == classroom.id)):
                continue
            recommendation, _ = await generate_recommendation(db, classroom.id)
            db.add_all([TimetableSlot(class_id=classroom.id, day_of_week=slot.day_of_week, period_number=slot.period_number, start_time=period_details[slot.period_number][0], end_time=period_details[slot.period_number][1], subject_id=slot.subject_id, teacher_id=slot.teacher_id) for slot in recommendation])
            await db.flush()
        demo_teacher = await db.scalar(select(User).where(User.email == "teacher@edusync.local"))
        if not demo_teacher:
            demo_teacher = User(email="teacher@edusync.local", password_hash=hash_password("Teacher@123"), full_name="Demo Teacher", role=UserRole.teacher, created_by=admin.id)
            db.add(demo_teacher); await db.flush(); db.add(TeacherProfile(user_id=demo_teacher.id))
            permission_keys = ["manage_students", "manage_assignments", "manage_exams", "manage_documents"]
            permission_rows = list((await db.scalars(select(Permission).where(Permission.key.in_(permission_keys)))).all())
            db.add_all([TeacherPermission(teacher_id=demo_teacher.id, permission_id=permission.id, granted_by=admin.id) for permission in permission_rows])
        else:
            permission_keys = ["manage_students", "manage_assignments", "manage_exams", "manage_documents"]
            permission_rows = list((await db.scalars(select(Permission).where(Permission.key.in_(permission_keys)))).all())
            for permission in permission_rows:
                if not await db.scalar(select(TeacherPermission.id).where(TeacherPermission.teacher_id == demo_teacher.id, TeacherPermission.permission_id == permission.id)):
                    db.add(TeacherPermission(teacher_id=demo_teacher.id, permission_id=permission.id, granted_by=admin.id))
        today = date.today()
        for full_name, email, student_code, roll_no, grade, section, card_uid in DEMO_ATTENDANCE_STUDENTS:
            demo_class = await db.scalar(select(ClassRoom).where(ClassRoom.grade == grade, ClassRoom.section == section))
            demo_student = await db.scalar(select(User).where(User.email == email))
            if not demo_student:
                demo_student = User(email=email, password_hash=hash_password("Student@123"), full_name=full_name, role=UserRole.student, created_by=demo_teacher.id)
                db.add(demo_student); await db.flush()
            elif demo_student.created_by != demo_teacher.id:
                demo_student.created_by = demo_teacher.id
            demo_profile = await db.get(StudentProfile, demo_student.id)
            if not demo_profile:
                demo_profile = StudentProfile(user_id=demo_student.id, class_id=demo_class.id, roll_no=roll_no, student_code=student_code, created_by=demo_teacher.id)
                db.add(demo_profile); await db.flush()
            elif demo_profile.created_by != demo_teacher.id:
                demo_profile.created_by = demo_teacher.id
            if not await db.scalar(select(RFIDCard).where(RFIDCard.uid == card_uid)):
                db.add(RFIDCard(uid=card_uid, student_id=demo_student.id, label=f"Demo NFC Card - {full_name}"))
            if not await db.scalar(select(AttendanceRecord.id).where(AttendanceRecord.student_id == demo_student.id)):
                marked_days = 0
                for offset, status in DEMO_ATTENDANCE_PATTERN:
                    db.add(AttendanceRecord(student_id=demo_student.id, class_id=demo_profile.class_id, attendance_date=today - timedelta(days=offset), status=status, source="demo", scan_uid=card_uid if status != AttendanceStatus.absent else None, scanned_at=datetime.now(timezone.utc) - timedelta(days=offset), notes="Demo attendance history"))
                    if status in (AttendanceStatus.present, AttendanceStatus.late):
                        marked_days += 1
                demo_profile.attendance_pct = Decimal(str(round((marked_days / len(DEMO_ATTENDANCE_PATTERN)) * 100, 2)))
        await db.commit()

if __name__ == "__main__": asyncio.run(seed())

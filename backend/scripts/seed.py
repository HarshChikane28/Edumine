import asyncio
from sqlalchemy import select
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import ClassRoom, Permission, Subject, TeacherProfile, TimetableSlot, User, UserRole
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

async def seed() -> None:
    async with SessionLocal() as db:
        if not await db.scalar(select(User).where(User.email == "admin@edusync.local")):
            db.add(User(email="admin@edusync.local", password_hash=hash_password("Admin@123"), full_name="EduSync Administrator", role=UserRole.admin))
        for key, description in PERMISSIONS.items():
            if not await db.scalar(select(Permission).where(Permission.key == key)): db.add(Permission(key=key, description=description))
        for grade, section in [("Grade 12", "A"), ("Grade 11", "A"), ("Grade 10", "B")]:
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
        await db.commit()

if __name__ == "__main__": asyncio.run(seed())

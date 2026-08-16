import asyncio
from sqlalchemy import select
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import ClassRoom, Permission, User, UserRole

PERMISSIONS = {"manage_students": "Create and edit student accounts and profiles", "manage_exams": "Create and edit exams and schedules", "enter_results": "Enter and edit student marks", "manage_timetable": "Create and edit timetable slots", "manage_assignments": "Create assignments and grade submissions", "manage_documents": "Approve and process document requests", "manage_activities": "Create and manage clubs and activities"}

async def seed() -> None:
    async with SessionLocal() as db:
        if not await db.scalar(select(User).where(User.email == "admin@edusync.local")):
            db.add(User(email="admin@edusync.local", password_hash=hash_password("Admin@123"), full_name="EduSync Administrator", role=UserRole.admin))
        for key, description in PERMISSIONS.items():
            if not await db.scalar(select(Permission).where(Permission.key == key)): db.add(Permission(key=key, description=description))
        for grade, section in [("Grade 12", "A"), ("Grade 11", "A"), ("Grade 10", "B")]:
            if not await db.scalar(select(ClassRoom).where(ClassRoom.grade == grade, ClassRoom.section == section)): db.add(ClassRoom(grade=grade, section=section))
        await db.commit()

if __name__ == "__main__": asyncio.run(seed())

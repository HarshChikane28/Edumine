from fastapi import APIRouter
router = APIRouter()

@router.get("/{student_id}/dashboard")
async def dashboard(student_id: str) -> dict:
    return {"student_id": student_id, "events": [{"title": "Science Exhibition", "countdown": "20 Days Left"}, {"title": "Annual Function Day", "countdown": "5 Days Left"}], "announcement": {"title": "School Holiday", "body": "The campus will remain closed this Friday."}, "progress": [65, 78, 58, 86, 72, 92, 80]}

@router.get("/{student_id}/profile")
async def profile(student_id: str) -> dict:
    return {"student_id": student_id, "name": "Shashi Kant", "class_name": "Grade 12 • Section A", "student_code": "STU-2024-018", "gpa": 4.2, "attendance": 94, "assignments_completed": 12}

@router.get("/{student_id}/insights")
async def insights(student_id: str) -> dict:
    return {"student_id": student_id, "title": "You're building strong momentum", "text": "Your performance in science subjects has improved by 12% this term."}

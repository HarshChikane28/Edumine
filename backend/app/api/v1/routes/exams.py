from fastapi import APIRouter
router = APIRouter()

@router.get("")
async def exams() -> dict:
    return {"summary": {"upcoming": 4, "average_score": 82, "grading_progress": 68}, "items": [{"subject": "Mathematics", "date": "Oct 24, 2024", "hall": "Hall A", "proctor": "Mr. Davis", "status": "Scheduled"}, {"subject": "Physics", "date": "Oct 26, 2024", "hall": "Hall B", "proctor": "Mrs. Chen", "status": "Scheduled"}]}

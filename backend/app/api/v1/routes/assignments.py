from fastapi import APIRouter
router = APIRouter()

@router.get("/{student_id}/assignments")
async def assignments(student_id: str, status: str | None = None) -> dict:
    items = [{"title": "Compiler Design Lab 4", "subject": "Compiler Design", "due": "Due tomorrow", "status": "Pending"}, {"title": "Flutter UI Prototype", "subject": "Mobile Application", "due": "Due Oct 30", "status": "Submitted"}, {"title": "Neural Networks Research Paper", "subject": "Artificial Intelligence", "due": "Due Nov 05", "status": "Graded"}]
    return {"student_id": student_id, "items": [item for item in items if not status or item["status"].lower() == status.lower()]}

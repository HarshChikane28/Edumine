from fastapi import APIRouter
router = APIRouter()

@router.get("/{student_id}")
async def result(student_id: str, exam_id: str | None = None) -> dict:
    return {"student_id": student_id, "exam_id": exam_id or "semester", "rank": 4, "gpa": 4.2, "result": "Passed", "subjects": [{"subject": "Mathematics", "marks": 92, "grade": "A+", "status": "Passed"}, {"subject": "Physics", "marks": 86, "grade": "A", "status": "Passed"}, {"subject": "Chemistry", "marks": 78, "grade": "B+", "status": "Passed"}]}

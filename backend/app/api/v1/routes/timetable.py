from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter()
class TimetablePayload(BaseModel):
    grade: str
    section: str
    slots: list[dict]

@router.get("")
async def timetable(grade: str = "12", section: str = "A") -> dict:
    return {"grade": grade, "section": section, "slots": []}

@router.put("")
async def save_timetable(payload: TimetablePayload) -> dict:
    return {"saved": True, **payload.model_dump()}

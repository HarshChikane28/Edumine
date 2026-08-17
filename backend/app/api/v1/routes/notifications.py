from fastapi import APIRouter, HTTPException

from app.services.notifications import list_notifications, mark_read


router = APIRouter()


@router.get("")
async def notifications(grade: str = "12", section: str = "A") -> list[dict]:
    return list_notifications(grade, section)


@router.patch("/{notification_id}/read")
async def read_notification(notification_id: str) -> dict:
    if not mark_read(notification_id):
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"read": True}

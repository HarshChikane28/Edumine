from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import require_permission
from app.db.session import get_db
from app.models import Activity, ActivityEnrollment, ActivityFeed, User

router = APIRouter()

@router.get("/dashboard")
async def activity_dashboard(_: User = Depends(require_permission("manage_activities")), db: AsyncSession = Depends(get_db)) -> dict:
    activities = list((await db.scalars(select(Activity))).all()); upcoming = []
    for activity in activities:
        enrolled = await db.scalar(select(func.count(ActivityEnrollment.id)).where(ActivityEnrollment.activity_id == activity.id))
        upcoming.append({"id": str(activity.id), "name": activity.name, "supervisor_id": str(activity.supervisor_id), "enrollment": enrolled or 0, "max_enrollment": activity.max_enrollment})
    feed = list((await db.scalars(select(ActivityFeed).order_by(ActivityFeed.created_at.desc()).limit(20))).all())
    return {"upcoming": upcoming, "top_performing": [], "feed": [{"text": item.text, "created_at": item.created_at} for item in feed]}

from fastapi import APIRouter
router = APIRouter()

@router.get("/dashboard")
async def activity_dashboard() -> dict:
    return {"upcoming": [{"name": "Debate Club", "next_date": "Oct 27", "supervisor": "Mrs. Chen", "enrollment": "45/50"}, {"name": "Soccer Match", "next_date": "Oct 28, 4:00 PM", "supervisor": "Mr. Davis", "enrollment": "22/25"}], "top_performing": [{"name": "Robotics Club", "performance": 98, "awards": 3}], "feed": [{"text": "Science Club submitted project report", "time": "Today, 10:30 AM"}]}

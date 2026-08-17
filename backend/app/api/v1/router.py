from fastapi import APIRouter
from app.api.v1.routes import activities, assignments, attendance, auth, documents, exams, notifications, profiles, results, students, timetable, admin_teachers

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin_teachers.router, prefix="/admin", tags=["admin"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(assignments.router, prefix="/students", tags=["assignments"])
api_router.include_router(results.router, prefix="/results", tags=["results"])
api_router.include_router(exams.router, prefix="/exams", tags=["exams"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(timetable.router, prefix="/timetable", tags=["timetable"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

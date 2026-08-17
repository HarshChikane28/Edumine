from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import assert_student_access, get_current_user, require_permission, require_role
from app.core.security import hash_password
from app.db.session import get_db
from app.models import Assignment, AssignmentSubmission, ClassRoom, Document, StudentProfile, User, UserRole
from app.core.config import settings
from app.services.storage import save_file
from app.schemas.admin import StudentCreate

router = APIRouter()

@router.post("/teachers/students")
async def create_student(payload: StudentCreate, teacher: User = Depends(require_permission("manage_students")), db: AsyncSession = Depends(get_db)) -> dict:
    if await db.scalar(select(User).where(User.email == payload.email.lower())): raise HTTPException(409, "Email already exists")
    profile_class = await db.get(ClassRoom, payload.class_id)
    if not profile_class: raise HTTPException(404, "Class not found")
    student = User(email=payload.email.lower(), password_hash=hash_password(payload.password), full_name=payload.full_name, role=UserRole.student, created_by=teacher.id)
    db.add(student); await db.flush(); db.add(StudentProfile(user_id=student.id, class_id=payload.class_id, roll_no=payload.roll_no, student_code=payload.student_code, created_by=teacher.id)); await db.commit()
    return {"id": str(student.id), "email": student.email, "role": student.role.value, "class_id": str(payload.class_id)}

@router.get("/teachers/students")
async def list_students(teacher: User = Depends(require_permission("manage_students")), db: AsyncSession = Depends(get_db)) -> list[dict]:
    profiles = list((await db.scalars(select(StudentProfile).where(StudentProfile.created_by == teacher.id))).all())
    if not profiles: return []
    users = {user.id: user for user in (await db.scalars(select(User).where(User.id.in_([profile.user_id for profile in profiles])))).all()}
    return [{"id": str(profile.user_id), "full_name": users[profile.user_id].full_name, "email": users[profile.user_id].email, "class_id": str(profile.class_id), "roll_no": profile.roll_no, "student_code": profile.student_code} for profile in profiles]

async def student_profile_or_404(student_id: UUID, user: User, db: AsyncSession) -> StudentProfile:
    await assert_student_access(student_id, user, db)
    profile = await db.get(StudentProfile, student_id)
    if not profile: raise HTTPException(404, "Student profile not found")
    return profile

@router.get("/{student_id}/dashboard")
async def dashboard(student_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    profile = await student_profile_or_404(student_id, user, db)
    assignments = await db.scalar(select(AssignmentSubmission).join(Assignment).where(Assignment.class_id == profile.class_id, AssignmentSubmission.student_id == student_id).limit(1))
    return {"student_id": str(student_id), "events": [], "announcement": None, "progress": [], "has_assignments": assignments is not None}

@router.get("/{student_id:uuid}/profile")
async def profile(student_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    return await profile_payload(student_id, user, db)

async def profile_payload(student_id: UUID, user: User, db: AsyncSession) -> dict:
    profile = await student_profile_or_404(student_id, user, db)
    account = await db.get(User, student_id)
    classroom = await db.get(ClassRoom, profile.class_id)
    personal_fields = ["first_name", "middle_name", "last_name", "date_of_birth", "gender", "blood_group", "marital_status", "nationality", "religion", "category", "caste", "sub_caste", "mother_tongue", "aadhaar_number", "pan_number", "personal_email", "alternate_mobile", "emergency_contact_name", "emergency_contact_number", "emergency_contact_relationship", "birth_place", "birth_country", "birth_state", "birth_district", "native_place", "native_country", "native_state", "native_district", "permanent_address", "current_address", "permanent_address_same"]
    personal = {"full_name": account.full_name, "email": account.email}
    for field in personal_fields:
        value = getattr(profile, field)
        personal[field] = value.isoformat() if isinstance(value, date) else value
    return {"student_id": str(student_id), "personal": personal, "academic": {"class_id": str(profile.class_id), "grade": classroom.grade if classroom else None, "section": classroom.section if classroom else None, "roll_no": profile.roll_no, "student_code": profile.student_code, "gpa": profile.gpa, "attendance_pct": profile.attendance_pct}, "available_fields": ["full_name", "email", "roll_no", *personal_fields]}

@router.get("/me/profile")
async def my_profile(user: User = Depends(require_role("student")), db: AsyncSession = Depends(get_db)) -> dict:
    return await profile_payload(user.id, user, db)

@router.patch("/me/profile")
async def update_my_profile(payload: dict, user: User = Depends(require_role("student")), db: AsyncSession = Depends(get_db)) -> dict:
    profile = await student_profile_or_404(user.id, user, db)
    if "full_name" in payload:
        value = str(payload["full_name"]).strip()
        if not value or len(value) > 200: raise HTTPException(400, "Full name must be between 1 and 200 characters")
        user.full_name = value
    if "email" in payload:
        value = str(payload["email"]).strip().lower()
        duplicate = await db.scalar(select(User).where(User.email == value, User.id != user.id))
        if not value or len(value) > 320: raise HTTPException(400, "A valid email is required")
        if duplicate: raise HTTPException(409, "Email already exists")
        user.email = value
    if "roll_no" in payload:
        value = str(payload["roll_no"]).strip()
        if not value or len(value) > 40: raise HTTPException(400, "Roll number must be between 1 and 40 characters")
        profile.roll_no = value
    editable_fields = {"first_name", "middle_name", "last_name", "date_of_birth", "gender", "blood_group", "marital_status", "nationality", "religion", "category", "caste", "sub_caste", "mother_tongue", "aadhaar_number", "pan_number", "personal_email", "alternate_mobile", "emergency_contact_name", "emergency_contact_number", "emergency_contact_relationship", "birth_place", "birth_country", "birth_state", "birth_district", "native_place", "native_country", "native_state", "native_district", "permanent_address", "current_address", "permanent_address_same"}
    for field in editable_fields:
        if field in payload:
            value = payload[field]
            if field in {"date_of_birth"} and value:
                try: value = date.fromisoformat(str(value))
                except ValueError: raise HTTPException(400, "Date of birth must be a valid date")
            setattr(profile, field, value)
    await db.commit()
    return await profile_payload(user.id, user, db)

STUDENT_DOCUMENT_TYPES = {"aadhaar": "Aadhaar Card", "birth-certificate": "Birth Certificate"}

async def student_documents(user: User, db: AsyncSession) -> list[dict]:
    categories = [f"student:{user.id}:{key}" for key in STUDENT_DOCUMENT_TYPES]
    rows = (await db.scalars(select(Document).where(Document.category.in_(categories)).order_by(Document.upload_date.desc()))).all()
    latest: dict[str, Document] = {}
    for row in rows: latest.setdefault(row.category.rsplit(":", 1)[-1], row)
    return [{"type": key, "label": label, "uploaded": key in latest, "id": str(latest[key].id) if key in latest else None, "filename": latest[key].filename if key in latest else None, "uploaded_at": latest[key].upload_date.isoformat() if key in latest and latest[key].upload_date else None} for key, label in STUDENT_DOCUMENT_TYPES.items()]

@router.get("/me/documents")
async def my_documents(user: User = Depends(require_role("student")), db: AsyncSession = Depends(get_db)) -> list[dict]:
    return await student_documents(user, db)

@router.post("/me/documents/{document_type}")
async def upload_my_document(document_type: str, file: UploadFile = File(...), user: User = Depends(require_role("student")), db: AsyncSession = Depends(get_db)) -> dict:
    if document_type not in STUDENT_DOCUMENT_TYPES: raise HTTPException(400, "Unsupported student document type")
    if file.content_type not in {"application/pdf", "image/png", "image/jpeg", "image/jpg"}: raise HTTPException(400, "Only PDFs and images are supported")
    relative_path = await save_file(file)
    old = (await db.scalars(select(Document).where(Document.category == f"student:{user.id}:{document_type}").order_by(Document.upload_date.desc()))).all()
    for row in old: await db.delete(row)
    new_doc = Document(filename=file.filename or STUDENT_DOCUMENT_TYPES[document_type], file_path=relative_path, category=f"student:{user.id}:{document_type}", status="completed")
    db.add(new_doc); await db.commit(); await db.refresh(new_doc)
    return {"type": document_type, "label": STUDENT_DOCUMENT_TYPES[document_type], "uploaded": True, "id": str(new_doc.id), "filename": new_doc.filename, "uploaded_at": new_doc.upload_date.isoformat() if new_doc.upload_date else None}

@router.get("/me/documents/{document_type}/view")
async def view_my_document(document_type: str, user: User = Depends(require_role("student")), db: AsyncSession = Depends(get_db)):
    if document_type not in STUDENT_DOCUMENT_TYPES: raise HTTPException(400, "Unsupported student document type")
    row = await db.scalar(select(Document).where(Document.category == f"student:{user.id}:{document_type}").order_by(Document.upload_date.desc()))
    if not row: raise HTTPException(404, "Document not uploaded")
    path = (Path(settings.storage_dir) / row.file_path).resolve(); root = Path(settings.storage_dir).resolve()
    if root not in path.parents or not path.is_file(): raise HTTPException(404, "Document file not found")
    return FileResponse(path, media_type="application/octet-stream", filename=row.filename)

@router.get("/{student_id}/insights")
async def insights(student_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    await student_profile_or_404(student_id, user, db)
    return {"student_id": str(student_id), "title": None, "text": None}

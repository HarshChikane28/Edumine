from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import Document, DocumentStatus, StaffProfile, User, UserRole
from app.services.storage import save_file

router = APIRouter()
ALLOWED_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/jpg"}
TEACHER_DOCUMENTS = {
    "aadhaar": ("Aadhaar Card", True), "pan": ("PAN Card", True),
    "birth-certificate": ("Birth Certificate", False), "passport": ("Passport", False),
    "photo": ("Passport Size Photograph", True), "educational-certificates": ("Educational Certificates", False),
    "degree": ("Degree Certificate", False), "diploma": ("Diploma Certificate", False),
    "marksheets": ("Mark Sheets", False), "bed-ded-med": ("B.Ed / D.Ed / M.Ed Certificate", False),
    "tet": ("TET Certificate", False), "ctet": ("CTET Certificate", False),
    "set-net": ("SET/NET Certificate", False), "experience-letter": ("Experience Letter", False),
    "previous-employment": ("Previous Employment Certificate", False), "relieving-letter": ("Relieving Letter", False),
    "appointment-letter": ("Appointment Letter", False), "joining-letter": ("Joining Letter", False),
    "police-verification": ("Police Verification Certificate", False), "character": ("Character Certificate", False),
    "medical-fitness": ("Medical Fitness Certificate", False), "address-proof": ("Address Proof", False),
    "bank-proof": ("Bank Passbook / Cancelled Cheque", False), "resume": ("Resume/CV", False), "other": ("Other Supporting Documents", False),
}
ADMIN_DOCUMENTS = {"aadhaar": ("Aadhaar Card", True)}

DETAIL_FIELDS = [
    "first_name", "middle_name", "last_name", "date_of_birth", "gender", "blood_group", "marital_status", "nationality", "religion", "category", "caste", "sub_caste", "mother_tongue", "aadhaar_number", "pan_number", "personal_email", "alternate_mobile", "emergency_contact_name", "emergency_contact_number", "emergency_contact_relationship", "birth_place", "birth_country", "birth_state", "birth_district", "native_place", "native_country", "native_state", "native_district", "permanent_address", "current_address", "permanent_address_same", "employee_id", "employee_code", "department", "designation", "subjects_taught", "class_grade_assigned", "joining_date", "employment_type", "employment_status", "qualification", "highest_qualification", "specialization", "university_college", "graduation_year", "teaching_experience", "previous_organization", "previous_designation", "work_experience", "salary_pay_grade", "reporting_manager", "branch_campus", "staff_type",
]

def _value(value):
    return value.isoformat() if hasattr(value, "isoformat") else value

async def _staff(user: User, db: AsyncSession) -> StaffProfile:
    record = await db.get(StaffProfile, user.id)
    if not record:
        record = StaffProfile(user_id=user.id)
        db.add(record)
        await db.flush()
    return record

def _payload(user: User, record: StaffProfile) -> dict:
    personal = {"full_name": user.full_name, "official_email": user.email}
    professional = {}
    for field in DETAIL_FIELDS:
        value = _value(getattr(record, field))
        if field in {"employee_id", "employee_code", "department", "designation", "subjects_taught", "class_grade_assigned", "joining_date", "employment_type", "employment_status", "qualification", "highest_qualification", "specialization", "university_college", "graduation_year", "teaching_experience", "previous_organization", "previous_designation", "work_experience", "salary_pay_grade", "reporting_manager", "branch_campus", "staff_type"}:
            professional[field] = value
        else:
            personal[field] = value
    if user.role == UserRole.teacher:
        professional.pop("salary_pay_grade", None)
    return {"role": user.role.value, "personal": personal, "professional": professional}

def _documents(user: User):
    return TEACHER_DOCUMENTS if user.role == UserRole.teacher else ADMIN_DOCUMENTS

async def _document_list(user: User, db: AsyncSession) -> list[dict]:
    definitions = _documents(user)
    prefix = f"{user.role.value}:{user.id}:"
    rows = (await db.scalars(select(Document).where(Document.category.like(f"{prefix}%")))).all()
    latest = {}
    for row in sorted(rows, key=lambda item: item.upload_date or 0, reverse=True):
        latest.setdefault(row.category.rsplit(":", 1)[-1], row)
    return [{"type": key, "label": label, "required": required, "status": "uploaded" if key in latest else ("required" if required else "optional"), "id": str(latest[key].id) if key in latest else None, "filename": latest[key].filename if key in latest else None, "uploaded_at": _value(latest[key].upload_date) if key in latest else None} for key, (label, required) in definitions.items()]

@router.get("/me")
async def get_profile(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role == UserRole.student:
        raise HTTPException(404, "Use the student profile endpoint")
    return _payload(user, await _staff(user, db))

@router.patch("/me")
async def update_profile(payload: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role == UserRole.student:
        raise HTTPException(403, "Student profiles use the student endpoint")
    record = await _staff(user, db)
    if "full_name" in payload:
        value = str(payload["full_name"]).strip()
        if not value or len(value) > 200: raise HTTPException(400, "Full name must be between 1 and 200 characters")
        user.full_name = value
    if "official_email" in payload:
        value = str(payload["official_email"]).strip().lower()
        duplicate = await db.scalar(select(User).where(User.email == value, User.id != user.id))
        if duplicate: raise HTTPException(409, "Email already exists")
        user.email = value
    for field in DETAIL_FIELDS:
        if field in payload:
            if field in {"employee_id", "employee_code"} and payload[field] is not None and user.role != UserRole.admin:
                continue
            setattr(record, field, payload[field])
    await db.commit()
    return _payload(user, record)

@router.get("/me/documents")
async def get_documents(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role == UserRole.student: raise HTTPException(403, "Students cannot access staff documents")
    return await _document_list(user, db)

@router.post("/me/documents/{document_type}")
async def upload_document(document_type: str, file: UploadFile = File(...), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role == UserRole.student: raise HTTPException(403, "Students cannot upload staff documents")
    definitions = _documents(user)
    if document_type not in definitions: raise HTTPException(400, "Unsupported document type")
    if file.content_type not in ALLOWED_TYPES: raise HTTPException(400, "Only PDFs and images are supported")
    relative_path = await save_file(file, module=f"{user.role.value}-documents")
    category = f"{user.role.value}:{user.id}:{document_type}"
    for row in (await db.scalars(select(Document).where(Document.category == category))).all():
        await db.delete(row)
    new_doc = Document(filename=file.filename or definitions[document_type][0], file_path=relative_path, category=category, status=DocumentStatus.completed)
    db.add(new_doc); await db.commit(); await db.refresh(new_doc)
    return {"type": document_type, "label": definitions[document_type][0], "status": "uploaded", "filename": new_doc.filename, "uploaded_at": _value(new_doc.upload_date)}

async def _owned_document(document_type: str, user: User, db: AsyncSession) -> Document:
    if user.role == UserRole.student or document_type not in _documents(user): raise HTTPException(403, "Document access denied")
    row = await db.scalar(select(Document).where(Document.category == f"{user.role.value}:{user.id}:{document_type}").order_by(Document.upload_date.desc()))
    if not row: raise HTTPException(404, "Document not uploaded")
    return row

@router.get("/me/documents/{document_type}/view")
async def view_document(document_type: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    row = await _owned_document(document_type, user, db)
    path, root = (Path(settings.storage_dir) / row.file_path).resolve(), Path(settings.storage_dir).resolve()
    if root not in path.parents or not path.is_file(): raise HTTPException(404, "Document file not found")
    return FileResponse(path, media_type="application/octet-stream", filename=row.filename)

@router.delete("/me/documents/{document_type}")
async def delete_document(document_type: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    row = await _owned_document(document_type, user, db)
    await db.delete(row); await db.commit()
    return {"deleted": True}

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import require_permission
from app.db.session import get_db
from app.models import DocumentRequest, User
from app.services.storage import save_file

router = APIRouter()

@router.get("")
async def documents(_: User = Depends(require_permission("manage_documents")), db: AsyncSession = Depends(get_db)) -> dict:
    rows = list((await db.scalars(select(DocumentRequest).order_by(DocumentRequest.requested_at.desc()))).all())
    return {"items": [{"id": str(row.id), "document": row.document_type, "category": row.category, "status": row.status.value, "requested_at": row.requested_at} for row in rows]}

@router.post("/upload")
async def upload(file: UploadFile = File(...), _: User = Depends(require_permission("manage_documents"))) -> dict:
    relative_path = await save_file(file)
    return {"filename": file.filename, "path": relative_path, "url": f"/files/{relative_path}"}

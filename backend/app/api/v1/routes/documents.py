from fastapi import APIRouter, File, UploadFile
from app.services.storage import save_file
router = APIRouter()

@router.get("")
async def documents() -> dict:
    return {"items": [{"document": "Transfer Certificate", "category": "Student records", "requested_by": "Anita Roy", "date": "Oct 22, 2024", "status": "Pending"}, {"document": "Fee Receipt Q3", "category": "Finance", "requested_by": "Ravi Kumar", "date": "Oct 21, 2024", "status": "Processing"}]}

@router.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    relative_path = await save_file(file)
    return {"filename": file.filename, "path": relative_path, "url": f"/files/{relative_path}"}

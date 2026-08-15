from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
from app.core.config import settings

def ensure_storage() -> None:
    Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)

async def save_file(file: UploadFile, module: str = "documents") -> str:
    ensure_storage()
    safe_name = Path(file.filename or "upload.bin").name
    relative = Path(module) / f"{uuid4()}-{safe_name}"
    destination = Path(settings.storage_dir) / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(await file.read())
    return relative.as_posix()

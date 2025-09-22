import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile
from core.config import settings

UPLOAD_DIR = Path(settings.file_url.upload_dir) 
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_file(file: UploadFile, subdir: str = "questions") -> str | None:
    """Save uploaded file and return public URL"""
    if not file:
        return None

    # Ensure subdir exists
    target_dir = UPLOAD_DIR / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique file name
    ext = Path(file.filename).suffix
    file_name = f"{uuid.uuid4()}{ext}"
    file_path = target_dir / file_name

    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Public URL (FastAPI serves /uploads/*)
    return f"{settings.file_url.http}/uploads/{subdir}/{file_name}"

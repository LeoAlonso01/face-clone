from fastapi import APIRouter, File, UploadFile, HTTPException
from ..main import UPLOAD_DIR, STATIC_DIR
import os
from datetime import datetime

router = APIRouter(tags=["Archivos"])  # expose /pdf at root for compatibility

@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    static_path = os.path.join(STATIC_DIR, filename)
    content = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    with open(static_path, "wb") as buffer:
        buffer.write(content)
    file_url = f"http://localhost:8000/static/pdfs/{filename}"
    return {"url": file_url}

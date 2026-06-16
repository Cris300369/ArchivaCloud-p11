import os
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException, UploadFile
from services.s3_service import upload_file_to_s3, list_files_from_s3, delete_file_from_s3

router = APIRouter(prefix="/api", tags=["files"])

@router.post("/upload")
async def upload_file(file: UploadFile):
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in [".mov", ".mp4"]:
        raise HTTPException(status_code=400, detail="Archivo prohibido")
        
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    
    max_size = 100 * 1024 * 1024  # 100 MB
    min_size = 1024
    if size > max_size or size < min_size:
        raise HTTPException(status_code=400, detail="Archivo muy grande o muy pequeño. Tamaño permitido: 1 KB - 100 MB")
        
    upload_file_to_s3(file.file, filename)
    return {"mensaje": "Archivo recibido y subido a S3", "filename": filename, "size": size}

@router.get("/files")
def get_files():
    archivos = list_files_from_s3()
    return {"mensaje": "Archivos listados correctamente", "archivos": archivos}

@router.delete("/files/{filename}")
def delete_file(filename: str):
    delete_file_from_s3(filename)
    return {"mensaje": f"Archivo {filename} eliminado exitosamente de S3"}

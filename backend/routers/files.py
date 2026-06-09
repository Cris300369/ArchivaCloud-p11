from fastapi import APIRouter
from services.s3_service import list_files_from_s3, delete_file_from_s3

router = APIRouter(prefix="/api/files", tags=["files"])

@router.get("")
@router.get("/")
def get_files():
    archivos = list_files_from_s3()
    return {"mensaje": "Archivos listados correctamente", "archivos": archivos}

@router.delete("/{filename}")
def delete_file(filename: str):
    delete_file_from_s3(filename)
    return {"mensaje": f"Archivo {filename} eliminado exitosamente de S3"}

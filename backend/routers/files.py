import os
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException, UploadFile
from services.s3_service import upload_file_to_s3, list_files_from_s3, delete_file_from_s3
from services.dynamo_service import save_hash, get_all_hashes, delete_hash_by_s3_key
import hashlib

router = APIRouter(prefix="/api", tags=["files"])

@router.post("/upload")
async def upload_file(file: UploadFile):
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in [".mov", ".mp4"]:
        raise HTTPException(status_code=400, detail="Archivo prohibido")
        
    size = file.size or 0
    if not (1024 <= size <= 100 * 1024 * 1024):
        raise HTTPException(status_code=400, detail="Archivo muy grande o muy pequeño. Tamaño permitido: 1 KB - 100 MB")
        
    content = file.file.read()
    hash_file = hashlib.md5(content).hexdigest()
    file.file.seek(0)
    
    upload_file_to_s3(file.file, filename)
    try:
        save_hash(hash_file, filename)
    except Exception as e:
        print("Error DynamoDB:", e)
        
    return {"mensaje": "Archivo recibido y subido a S3", "filename": filename, "size": size, "hash": hash_file}

@router.get("/files")
def get_files():
    s3_files = list_files_from_s3()
    db_items = get_all_hashes()
    
    hash_to_keys = {}
    key_to_hash = {}
    for item in db_items:
        h, k = item.get("hash_file"), item.get("s3_key")
        if h and k:
            hash_to_keys.setdefault(h, []).append(k)
            key_to_hash[k] = h
            
    for f in s3_files:
        k = f["name"]
        h = key_to_hash.get(k)
        dups = [x for x in hash_to_keys.get(h, []) if x != k] if h else []
        f["duplicate"] = bool(dups)
        f["duplicates_list"] = dups
        
    return {"mensaje": "Archivos listados correctamente", "archivos": s3_files}

@router.delete("/files/{filename}")
def delete_file(filename: str):
    delete_file_from_s3(filename)
    try:
        delete_hash_by_s3_key(filename)
    except Exception as e:
        print("Error DynamoDB:", e)
    return {"mensaje": f"Archivo {filename} eliminado exitosamente de S3"}

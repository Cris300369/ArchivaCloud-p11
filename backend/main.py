from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "DELETE"],
    allow_headers=["*"],
)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
    aws_session_token=os.getenv("aws_session_token"),
    region_name=os.getenv("aws_region")
)

@app.post("/api/upload")
async def upload_file(file: UploadFile):
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in [".mov", ".mp4"]:
        raise HTTPException(status_code=400, detail="Archivo prohibido")
        
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    
    if size > 102400 or size < 1024:
        raise HTTPException(status_code=400, detail="Archivo muy grande o muy pequeño")
        
    bucket_name = os.getenv("s3_bucket")
    
    try:
        s3_client.upload_fileobj(file.file, bucket_name, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir archivo a S3: {str(e)}")

    return {"mensaje": "Archivo recibido y subido a S3", "filename": filename, "size": size}

@app.get("/healthz")
def health_check():
    try:
        s3_client.list_buckets()
        return {"mensaje": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="AWS S3 no disponible")
# pyrefly: ignore [missing-import]
from fastapi import FastAPI as fa
# pyrefly: ignore [missing-import]
from fastapi import HTTPException, UploadFile
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
import boto3
import os

load_dotenv()
app = fa()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    region_name=os.getenv("AWS_REGION")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST","GET","DELETE"],
    allow_headers=["*"],
)

class File(BaseModel):
    name: str = Field(description="nombre del archivo")
    type: str = Field(description="tipo del archivo")
    hash: str = Field(description="hash del archivo")
    size: int = Field(description="tamaño del archivo")
    url_aws: str = Field(description="url del archivo en aws")

files_upload = [
    File(
        name='trailer_pelicula.mp4',
        type='.mp4',
        hash='a7c2f8d9e1b4c6f3a8d7e2c1b5f9a4d6',
        size=51200,
        url_aws='https://bucket-ejemplo.s3.amazonaws.com/videos/trailer_pelicula.mp4'
    ),
    File(
        name='presentacion.mov',
        type='.mov',
        hash='f9b3d7c2a5e8b1d4c6f9a2e7b3c5d8f1',
        size=24576,
        url_aws='https://bucket-ejemplo.s3.amazonaws.com/videos/presentacion.mov'
    ),
    File(
        name='curso_python.mp4',
        type='.mp4',
        hash='d4a8c1f7b3e9d2a5c6f8b1e4d7a9c2f5',
        size=76800,
        url_aws='https://bucket-ejemplo.s3.amazonaws.com/videos/curso_python.mp4'
    ),
    File(
        name='demo_app.mov',
        type='.mov',
        hash='c5e9a2d7f1b4c8a3d6f9b2e5c7a1d4f8',
        size=15360,
        url_aws='https://bucket-ejemplo.s3.amazonaws.com/videos/demo_app.mov'
    ),
    File(
        name='documental.mp4',
        type='.mp4',
        hash='b8d2f5a1c4e7d9b3f6a8c2e5d1f4b7a9',
        size=102400,
        url_aws='https://bucket-ejemplo.s3.amazonaws.com/videos/documental.mp4'
    ),
    File(
        name='trailer_backup.mp4',
        type='.mp4',
        hash='a7c2f8d9e1b4c6f3a8d7e2c1b5f9a4d6',
        size=51200,
        url_aws='https://bucket-ejemplo.s3.amazonaws.com/videos/trailer_backup.mp4'
    ),
    File(
        name='presentacion_copia.mov',
        type='.mov',
        hash='f9b3d7c2a5e8b1d4c6f9a2e7b3c5d8f1',
        size=24576,
        url_aws='https://bucket-ejemplo.s3.amazonaws.com/videos/presentacion_copia.mov'
    )
]

@app.post('/api/upload')
async def upload_file(file: File):
    if not (file.type.lower() == ".mov" or file.type.lower() == ".mp4"):
        raise HTTPException(status_code=400, detail="Archivo prohibido")
    if not file.size > 102400 or file.size < 1024:
        raise HTTPException(status_code=400, detail="Archivo muy grande")
    return {"mensaje": "Archivo recibido", "file": file.model_dump()}

@app.get('/api/files')
def files():
    return {"mensaje": {i: file.model_dump() for i, file in enumerate(files_upload)}}

@app.get("/healthz")
def health_check():
    try:
        s3_client.list_buckets()
        return {"mensaje": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="AWS S3 no disponible")
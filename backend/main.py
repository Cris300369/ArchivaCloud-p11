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

@app.get('/api/files')
def files():
    bucket_name = os.getenv("s3_bucket")
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        archivos = []
        if 'Contents' in response:
            for obj in response['Contents']:
                url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': obj['Key']},
                    ExpiresIn=3600
                )
                archivos.append({
                    "name": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat(),
                    "url_aws": url
                })
        return {"mensaje": "Archivos listados correctamente", "archivos": archivos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener archivos de S3: {str(e)}")

@app.delete("/api/files/{filename}")
def delete_file(filename: str):
    bucket_name = os.getenv("s3_bucket")
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=filename)
        return {"mensaje": f"Archivo {filename} eliminado exitosamente de S3"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al borrar archivo de S3: {str(e)}")

@app.get("/healthz")
def health_check():
    try:
        s3_client.list_buckets()
        return {"mensaje": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="AWS S3 no disponible")
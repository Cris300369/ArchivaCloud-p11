from fastapi import FastAPI
from dotenv import load_dotenv
import boto3
import os

# Cargar variables del archivo .env
load_dotenv()

app = FastAPI()

# Cliente S3
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    region_name=os.getenv("AWS_REGION")
)

@app.get("/")
def root():
    return {
        "message": "ArchivaCloud P-11 funcionando"
    }

@app.get("/healthz")
def health():
    return {
        "status": "ok"
    }

@app.get("/env-test")
def env_test():
    return {
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
        "AWS_REGION": os.getenv("AWS_REGION"),
        "S3_BUCKET": os.getenv("S3_BUCKET")
    }

@app.get("/bucket-test")
def bucket_test():
    bucket_name = os.getenv("S3_BUCKET")

    try:
        s3_client.list_objects_v2(
            Bucket=bucket_name,
            MaxKeys=1
        )

        return {
            "status": "success",
            "bucket": bucket_name
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
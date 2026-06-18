import boto3
# pyrefly: ignore [missing-import]
from fastapi import HTTPException
from core.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_REGION, S3_BUCKET

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION
)

def upload_file_to_s3(file_obj, filename: str):
    try:
        s3_client.upload_fileobj(file_obj, S3_BUCKET, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir archivo a S3: {str(e)}")

def check_s3_health():
    try:
        s3_client.list_buckets()
        return True
    except Exception:
        return False

def list_files_from_s3():
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
        return [
            {
                "name": obj['Key'],
                "size": obj['Size'],
                "last_modified": obj['LastModified'].isoformat(),
                "url_aws": s3_client.generate_presigned_url(
                    'get_object', Params={'Bucket': S3_BUCKET, 'Key': obj['Key']}, ExpiresIn=3600
                )
            }
            for obj in response.get('Contents', [])
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener archivos de S3: {str(e)}")

def delete_file_from_s3(filename: str):
    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al borrar archivo de S3: {str(e)}")

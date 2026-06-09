# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException
from services.s3_service import check_s3_health

router = APIRouter(tags=["health"])

@router.get("/healthz")
def health_check():
    if check_s3_health():
        return {"mensaje": "ok"}
    else:
        raise HTTPException(status_code=503, detail="AWS S3 no disponible")

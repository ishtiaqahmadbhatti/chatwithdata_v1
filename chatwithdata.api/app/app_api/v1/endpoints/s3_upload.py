from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.app_services.s3_service import s3_service
from app.app_core.config import settings
import uuid

router = APIRouter()

class PresignedUrlRequest(BaseModel):
    filename: str
    content_type: str = None

class PresignedUrlResponse(BaseModel):
    upload_url: str
    file_key: str

@router.post("/generate-presigned-url", response_model=PresignedUrlResponse)
async def generate_presigned_url(request: PresignedUrlRequest):
    """
    Generate a presigned URL for direct S3 upload.
    Use this for files > 10MB to bypass API Gateway limits.
    """
    if not settings.s3_bucket:
        raise HTTPException(status_code=500, detail="S3 storage not configured")
    
    # Generate a unique key to avoid collisions
    file_extension = request.filename.split('.')[-1] if '.' in request.filename else ''
    unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
    file_key = f"uploads/{unique_filename}"
    
    url = s3_service.generate_presigned_upload_url(unique_filename, request.content_type)
    
    if not url:
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")
        
    return PresignedUrlResponse(upload_url=url, file_key=file_key)

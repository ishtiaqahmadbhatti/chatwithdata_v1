import logging
from fastapi import APIRouter, HTTPException, Depends, Form, Request, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.app_core.database import get_db
from app.app_api.v1.dependencies import get_user_id
from app.app_services.youtube_service import YouTubeService
from app.app_services.conversion_log_service import ConversionLogService
from app.app_services.file_service import FileService
from app.app_core.exceptions import create_error_response

logger = logging.getLogger(__name__)
router = APIRouter()


# ─────────────────────────────────────────────
# 1. Extract comprehensive data
# ─────────────────────────────────────────────
@router.post("/extract-data")
async def extract_youtube_data(
    request: Request,
    url: str = Form(...),
    fetch_comments: bool = Form(True),
    fetch_transcript: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Extract comprehensive data from a YouTube video including metadata,
    transcript, and comments.
    """
    log_id = None
    try:
        user_id = await get_user_id(request, db)

        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="youtube-extraction",
            input_filename=url,
            input_file_size=0,
            input_file_type="youtube_url",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        data = YouTubeService.get_video_data(
            url=url,
            fetch_comments=fetch_comments,
            fetch_transcript=fetch_transcript
        )

        ConversionLogService.update_log_status(
            db=db, log_id=log_id, status="success",
            output_filename="json_metadata", output_file_type="json"
        )

        return {"success": True, "data": data, "message": "YouTube data extracted successfully"}

    except ValueError as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="ValidationError", message=str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error in extract_youtube_data: {e}")
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="ExtractionError", message="Failed to extract YouTube data", details={"error": str(e)}, status_code=500)


# ─────────────────────────────────────────────
# 2. Download YouTube video / audio
# ─────────────────────────────────────────────
@router.post("/download")
async def download_youtube_video(
    request: Request,
    background_tasks: BackgroundTasks,
    url: str = Form(...),
    output_format: str = Form("mp4"),
    quality: str = Form("best"),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Download a YouTube video or audio track.

    - **output_format**: mp4 | mkv | webm | mp3 | wav | m4a | aac | flac
    - **quality**: best | worst | 1080p | 720p | 480p | 360p
    - **output_filename**: optional custom name (without extension)
    """
    log_id = None
    try:
        user_id = await get_user_id(request, db)

        if not ("youtube.com" in url or "youtu.be" in url):
            raise ValueError("Invalid YouTube URL")

        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="youtube-download",
            input_filename=url,
            input_file_size=0,
            input_file_type="youtube_url",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        result = YouTubeService.download_video(
            url=url,
            output_format=output_format,
            quality=quality,
            output_filename=output_filename,
        )

        filename = result["filename"]
        ConversionLogService.update_log_status(
            db=db, log_id=log_id, status="success",
            output_filename=filename, output_file_type=output_format
        )

        return {
            "success": True,
            "message": f"YouTube video downloaded successfully as {output_format.upper()}",
            "video_title": result["video_title"],
            "output_filename": filename,
            "format": output_format,
            "quality": quality,
            "download_url": f"/api/v1/youtubetools/download-file/{filename}",
        }

    except ValueError as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="ValidationError", message=str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error in download_youtube_video: {e}")
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="DownloadError", message=str(e), details={"error": str(e)}, status_code=500)


# ─────────────────────────────────────────────
# 3. Serve the downloaded file
# ─────────────────────────────────────────────
@router.get("/download-file/{filename}")
async def serve_downloaded_file(filename: str, background_tasks: BackgroundTasks):
    """Download the processed YouTube file and clean up after delivery."""
    import os
    from app.app_core.config import settings
    file_path = os.path.join(settings.output_dir, filename)
    return FileService.create_cleanup_response(file_path, filename, background_tasks)

import logging
from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
from app.app_services.youtube_service import YouTubeService
from app.app_services.file_service import FileService
from app.app_core.exceptions import create_error_response

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Request / Response schemas ─────────────────────────────────────────────────

class ExtractDataRequest(BaseModel):
    url: str = Field(..., description="The YouTube video URL")
    fetch_comments: bool = Field(True, description="Whether to fetch video comments")
    fetch_transcript: bool = Field(True, description="Whether to fetch video transcript")


class DownloadVideoRequest(BaseModel):
    url: str = Field(..., description="The YouTube video URL")
    output_format: str = Field("mp4", description="Output format (e.g., mp4, mp3)")
    quality: str = Field("best", description="Quality preset (e.g., best, worst)")
    output_filename: Optional[str] = Field(None, description="Optional custom output filename")


# ─────────────────────────────────────────────
# 1. Extract comprehensive data
# ─────────────────────────────────────────────
@router.post("/extract-data")
async def extract_youtube_data(
    body: ExtractDataRequest,
    request: Request
):
    """
    Extract comprehensive data from a YouTube video including metadata, transcript, and comments.
    """
    try:
        data = YouTubeService.get_video_data(
            url=body.url,
            fetch_comments=body.fetch_comments,
            fetch_transcript=body.fetch_transcript
        )
        return {"success": True, "data": data, "message": "YouTube data extracted successfully"}

    except ValueError as e:
        raise create_error_response(error_type="ValidationError", message=str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error in extract_youtube_data: {e}")
        raise create_error_response(error_type="ExtractionError", message="Failed to extract YouTube data", details={"error": str(e)}, status_code=500)


# ─────────────────────────────────────────────
# 2. Download YouTube video / audio
# ─────────────────────────────────────────────
@router.post("/download")
async def download_youtube_video(
    body: DownloadVideoRequest,
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Download a YouTube video or audio track.

    - **url**: The YouTube video URL
    - **output_format**: mp4 | mkv | webm | mp3 | wav | m4a | aac | flac
    - **quality**: best | worst | 1080p | 720p | 480p | 360p
    - **output_filename**: optional custom name (without extension)
    """
    try:
        if not ("youtube.com" in body.url or "youtu.be" in body.url):
            raise ValueError("Invalid YouTube URL")

        result = YouTubeService.download_video(
            url=body.url,
            output_format=body.output_format,
            quality=body.quality,
            output_filename=body.output_filename,
        )

        filename = result["filename"]
        return {
            "success": True,
            "message": f"YouTube video downloaded successfully as {body.output_format.upper()}",
            "video_title": result["video_title"],
            "output_filename": filename,
            "format": body.output_format,
            "quality": body.quality,
            "download_url": f"/api/v1/youtubetools/download-file/{filename}",
        }

    except ValueError as e:
        raise create_error_response(error_type="ValidationError", message=str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error in download_youtube_video: {e}")
        raise create_error_response(error_type="DownloadError", message=str(e), details={"error": str(e)}, status_code=500)


# ─────────────────────────────────────────────
# 3. Serve the downloaded file
# ─────────────────────────────────────────────
from fastapi.responses import FileResponse

@router.get(
    "/download-file/{filename}",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "description": "Returns the raw binary file stream.",
        },
        404: {
            "content": {"application/json": {}},
            "description": "File not found error.",
        }
    }
)
async def serve_downloaded_file(filename: str, background_tasks: BackgroundTasks):
    """Download the processed YouTube file and clean up after delivery."""
    import os
    from app.app_core.config import settings
    file_path = os.path.join(settings.output_dir, filename)
    return FileService.create_cleanup_response(file_path, filename, background_tasks)

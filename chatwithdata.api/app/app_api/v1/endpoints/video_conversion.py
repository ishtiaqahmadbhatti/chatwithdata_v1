import os
import shutil
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form, Query, Request, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional, Union
from sqlalchemy.orm import Session
from app.app_core.database import get_db
from app.app_api.v1.dependencies import get_user_id
from app.app_services.conversion_log_service import ConversionLogService

from app.app_models.schemas import ConversionResponse
from app.app_services.video_conversion_service import VideoConversionService
from app.app_core.exceptions import (
    FileProcessingError, 
    UnsupportedFileTypeError, 
    FileSizeExceededError,
    create_error_response
)
from app.app_services.file_service import FileService
from app.app_core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

def _build_download_url(filename: str) -> str:
    """Build consistent download url for generated files."""
    return f"/api/v1/videoconversiontools/download/{filename}"


async def _handle_video_conversion(
    request: Request,
    db: Session,
    file: Optional[UploadFile] = None,
    file_key: Optional[str] = None,
    output_format: str = "mp4",
    tool_name: str = "video-conversion",
    output_filename: Optional[str] = None,
    **kwargs
) -> ConversionResponse:
    """Helper to handle generic video conversion."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_type = tool_name.split("-")[0] if "-" in tool_name else "video"
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, input_type)
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type=tool_name,
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type=input_filename.split('.')[-1].lower() if '.' in input_filename else input_type,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (output_filename or input_filename).strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=f".{output_format.lower()}",
        )
        
        # Dispatch to correct service method
        method_name = tool_name.replace("-", "_")
        if hasattr(VideoConversionService, method_name):
            method = getattr(VideoConversionService, method_name)
            
            # Most video service methods take (input_path, extra_arg)
            # extra_arg is typically quality (MOV->MP4) or bitrate (MP4->MP3)
            extra_arg = kwargs.get("quality") or kwargs.get("bitrate") or kwargs.get("format")
            
            if extra_arg:
                temp_output_path = method(input_path, extra_arg)
            else:
                temp_output_path = method(input_path)
                
            output_path = temp_output_path
        else:
            raise UnsupportedFileTypeError(f"Unsupported tool: {tool_name}")
            
        # Get output file size
        output_file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type=output_format.lower(),
            output_file_size=output_file_size
        )
        
        # Final rename to final location
        target_path = os.path.join(settings.output_dir, final_filename)
        if os.path.abspath(output_path) != os.path.abspath(target_path):
             if os.path.exists(target_path): os.remove(target_path)
             shutil.move(output_path, target_path)

        success = True
        return ConversionResponse(
            success=True,
            message=f"File converted to {output_format.upper()} successfully",
            output_filename=final_filename,
            download_url=_build_download_url(final_filename)
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else output_path)

# 1. MOV to MP4
@router.post("/mov-to-mp4", response_model=ConversionResponse)
async def convert_mov_to_mp4(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    quality: str = Form("medium"),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert MOV file to MP4 format."""
    return await _handle_video_conversion(
        request, db, file, file_key, "mp4", "mov-to-mp4", output_filename, quality=quality
    )

# 2. MKV to MP4
@router.post("/mkv-to-mp4", response_model=ConversionResponse)
async def convert_mkv_to_mp4(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    quality: str = Form("medium"),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert MKV file to MP4 format."""
    return await _handle_video_conversion(
        request, db, file, file_key, "mp4", "mkv-to-mp4", output_filename, quality=quality
    )

# 3. AVI to MP4
@router.post("/avi-to-mp4", response_model=ConversionResponse)
async def convert_avi_to_mp4(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    quality: str = Form("medium"),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert AVI file to MP4 format."""
    return await _handle_video_conversion(
        request, db, file, file_key, "mp4", "avi-to-mp4", output_filename, quality=quality
    )

# 4. MP4 to MP3
@router.post("/mp4-to-mp3", response_model=ConversionResponse)
async def convert_mp4_to_mp3(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    bitrate: str = Form("192k"),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert MP4 file to MP3 audio format."""
    return await _handle_video_conversion(
        request, db, file, file_key, "mp3", "mp4-to-mp3", output_filename, bitrate=bitrate
    )


@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported input and output formats."""
    try:
        formats = VideoConversionService.get_supported_formats()
        return {
            "success": True,
            "formats": formats,
            "message": "Supported formats retrieved successfully"
        }
    except Exception as e:
        raise create_error_response(
            error_type="InternalServerError",
            message="Failed to retrieve supported formats",
            details={"error": str(e)},
            status_code=500
        )


@router.post("/download-youtube", response_model=ConversionResponse)
async def download_youtube_video(
    request: Request,
    url: str = Form(...),
    quality: str = Form("best"),
    format: str = Form("mp4"),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Download YouTube video by URL."""
    import yt_dlp
    output_path = None
    log_id = None
    success = False
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="download-youtube",
            input_filename=url,
            input_file_size=0,
            input_file_type="youtube_url",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Validate YouTube URL
        if not ("youtube.com" in url or "youtu.be" in url):
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        # Prepare output filename
        final_filename = output_filename.strip() if output_filename and output_filename.strip() else f"youtube_video.{format}"
        if not final_filename.endswith(f".{format}"):
            final_filename += f".{format}"
        
        # Use a temporary name for yt-dlp download
        temp_base = f"yt_temp_{os.urandom(4).hex()}"
        temp_output_template = os.path.join(settings.output_dir, f"{temp_base}.%(ext)s")
        
        # Determine format string based on quality and format
        if format == 'mp3': format_string = 'bestaudio/best'
        elif quality == 'best': format_string = 'bestvideo+bestaudio/best'
        elif quality == 'worst': format_string = 'worstvideo+worstaudio/worst'
        elif quality.endswith('p'):
            height = quality.replace('p', '')
            format_string = f'bestvideo[height<={height}]+bestaudio/best'
        else: format_string = 'bestvideo+bestaudio/best'
        
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        
        ydl_opts = {
            'format': format_string,
            'outtmpl': temp_output_template,
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': ffmpeg_path,
        }
        
        if format == 'mp3':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif format != 'mp4':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': format,
            }]
        
        # Download video
        downloaded_file = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'video')
            
            if not output_filename or not output_filename.strip():
                safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title[:50]
                if safe_title: final_filename = f"{safe_title}.{format}"
        
        # Find the downloaded file
        for f in os.listdir(settings.output_dir):
            if f.startswith(temp_base):
                downloaded_file = os.path.join(settings.output_dir, f)
                break
        
        if not downloaded_file or not os.path.exists(downloaded_file):
            raise FileProcessingError("Downloaded file not found")
        
        # Rename to final filename
        target_path = os.path.join(settings.output_dir, final_filename)
        if os.path.exists(target_path): os.remove(target_path)
        shutil.move(downloaded_file, target_path)
        output_path = target_path
        
        # Get file size
        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type=format,
            output_file_size=file_size
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message=f"YouTube video downloaded successfully as {format.upper()}",
            output_filename=final_filename,
            download_url=_build_download_url(final_filename)
        )
        
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="DownloadError", message=str(e), status_code=400)
    finally:
        if not success and output_path:
            FileService.cleanup_file(output_path)


@router.get("/download/{filename}")
async def download_file(filename: str, background_tasks: BackgroundTasks):
    """Download converted file and clean up."""
    file_path = os.path.join(settings.output_dir, filename)
    return FileService.create_cleanup_response(file_path, filename, background_tasks)

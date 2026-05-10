import os
import shutil
import json
import logging
from typing import Optional, Union
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends, Request, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.app_core.database import get_db
from app.app_api.v1.dependencies import get_user_id
from app.app_services.conversion_log_service import ConversionLogService

from app.app_core.config import settings
from app.app_models.schemas import ConversionResponse
from app.app_services.audio_conversion_service import AudioConversionService
from app.app_core.exceptions import (
    FileProcessingError,
    UnsupportedFileTypeError,
    FileSizeExceededError,
    create_error_response
)
from app.app_services.file_service import FileService

logger = logging.getLogger(__name__)
router = APIRouter()

def _build_download_url(filename: str) -> str:
    """Build consistent download url for generated files."""
    return f"/api/v1/audioconversiontools/download/{filename}"


# 1. MP4 to MP3
@router.post("/mp4-to-mp3", response_model=ConversionResponse)
async def convert_mp4_to_mp3(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    bitrate: str = Form("192k"),
    quality: str = Form("medium"),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert MP4 file to MP3 format."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "video")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="mp4-to-mp3",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="mp4",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (output_filename or input_filename).strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".mp3",
        )
        
        # Convert
        temp_output_path = AudioConversionService.mp4_to_mp3(input_path, bitrate, quality)
        output_path = temp_output_path
        
        # Get output file size
        output_file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="mp3",
            output_file_size=output_file_size
        )
        
        # Final rename
        target_path = os.path.join(settings.output_dir, final_filename)
        if os.path.abspath(output_path) != os.path.abspath(target_path):
             if os.path.exists(target_path): os.remove(target_path)
             shutil.move(output_path, target_path)

        success = True
        return ConversionResponse(
            success=True,
            message="MP4 file converted to MP3 successfully",
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


# 2. WAV to MP3
@router.post("/wav-to-mp3", response_model=ConversionResponse)
async def convert_wav_to_mp3(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    bitrate: str = Form("192k"),
    quality: str = Form("medium"),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert WAV file to MP3 format."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "audio")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="wav-to-mp3",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="wav",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (output_filename or input_filename).strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".mp3",
        )
        
        # Convert
        temp_output_path = AudioConversionService.wav_to_mp3(input_path, bitrate, quality)
        output_path = temp_output_path
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="mp3"
        )
        
        # Final rename
        target_path = os.path.join(settings.output_dir, final_filename)
        if os.path.abspath(output_path) != os.path.abspath(target_path):
             if os.path.exists(target_path): os.remove(target_path)
             shutil.move(output_path, target_path)

        success = True
        return ConversionResponse(
            success=True,
            message="WAV file converted to MP3 successfully",
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


# 3. FLAC to MP3
@router.post("/flac-to-mp3", response_model=ConversionResponse)
async def convert_flac_to_mp3(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    bitrate: str = Form("192k"),
    quality: str = Form("medium"),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert FLAC file to MP3 format."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "audio")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="flac-to-mp3",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="flac",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (output_filename or input_filename).strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".mp3",
        )
        
        # Convert
        temp_output_path = AudioConversionService.flac_to_mp3(input_path, bitrate, quality)
        output_path = temp_output_path
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="mp3"
        )
        
        # Final rename
        target_path = os.path.join(settings.output_dir, final_filename)
        if os.path.abspath(output_path) != os.path.abspath(target_path):
             if os.path.exists(target_path): os.remove(target_path)
             shutil.move(output_path, target_path)

        success = True
        return ConversionResponse(
            success=True,
            message="FLAC file converted to MP3 successfully",
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


# 4. MP3 to WAV
@router.post("/mp3-to-wav", response_model=ConversionResponse)
async def convert_mp3_to_wav(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    sample_rate: int = Form(44100),
    channels: int = Form(2),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert MP3 file to WAV format."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "audio")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="mp3-to-wav",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="mp3",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (output_filename or input_filename).strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".wav",
        )
        
        # Convert
        temp_output_path = AudioConversionService.mp3_to_wav(input_path, sample_rate, channels)
        output_path = temp_output_path
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="wav"
        )
        
        # Final rename
        target_path = os.path.join(settings.output_dir, final_filename)
        if os.path.abspath(output_path) != os.path.abspath(target_path):
             if os.path.exists(target_path): os.remove(target_path)
             shutil.move(output_path, target_path)

        success = True
        return ConversionResponse(
            success=True,
            message="MP3 file converted to WAV successfully",
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


# 5. FLAC to WAV
@router.post("/flac-to-wav", response_model=ConversionResponse)
async def convert_flac_to_wav(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    sample_rate: int = Form(44100),
    channels: int = Form(2),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert FLAC file to WAV format."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "audio")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="flac-to-wav",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="flac",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (output_filename or input_filename).strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".wav",
        )
        
        # Convert
        temp_output_path = AudioConversionService.flac_to_wav(input_path, sample_rate, channels)
        output_path = temp_output_path
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="wav"
        )
        
        # Final rename
        target_path = os.path.join(settings.output_dir, final_filename)
        if os.path.abspath(output_path) != os.path.abspath(target_path):
             if os.path.exists(target_path): os.remove(target_path)
             shutil.move(output_path, target_path)

        success = True
        return ConversionResponse(
            success=True,
            message="FLAC file converted to WAV successfully",
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


# 6. WAV to FLAC
@router.post("/wav-to-flac", response_model=ConversionResponse)
async def convert_wav_to_flac(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    compression_level: int = Form(5),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert WAV file to FLAC format."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "audio")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="wav-to-flac",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="wav",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (output_filename or input_filename).strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".flac",
        )
        
        # Convert
        temp_output_path = AudioConversionService.wav_to_flac(input_path, compression_level)
        output_path = temp_output_path
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="flac"
        )
        
        # Final rename
        target_path = os.path.join(settings.output_dir, final_filename)
        if os.path.abspath(output_path) != os.path.abspath(target_path):
             if os.path.exists(target_path): os.remove(target_path)
             shutil.move(output_path, target_path)

        success = True
        return ConversionResponse(
            success=True,
            message="WAV file converted to FLAC successfully",
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


# 7. Trim Audio
@router.post("/trim-audio", response_model=ConversionResponse)
async def trim_audio(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    segments: str = Form(...), # JSON string: '[{"start": "00:03", "end": "01:04"}, ...]'
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Trim audio to specified time segments and merge them."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "audio")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="trim-audio",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="audio",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Parse segments
        segments_list = []
        try:
            # Try JSON first
            decoded = json.loads(segments)
            if isinstance(decoded, list): segments_list = decoded
            elif isinstance(decoded, dict): segments_list = [decoded]
            else: raise ValueError("JSON must be a list or object")
        except json.JSONDecodeError:
             # Try simple string format: "start-end" or "start-end,start-end"
             try:
                 parts = segments.split(',')
                 for part in parts:
                     if '-' in part:
                         start, end = part.split('-', 1)
                         segments_list.append({"start": start.strip(), "end": end.strip()})
                     else: raise ValueError("Missing separator '-'")
             except Exception: raise FileProcessingError("Invalid segments format. Use JSON or 'start-end'.")
        except Exception as e: raise FileProcessingError(f"Invalid segments format: {str(e)}")

        if not segments_list: raise FileProcessingError("No valid segments provided")

        # Determine output extension from input file
        _, input_ext = os.path.splitext(input_filename)
        target_ext = input_ext.lstrip('.') if input_ext else "mp3"
        
        # Determine output filename
        desired_name = (output_filename or input_filename).strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=f".{target_ext}",
        )
        
        # Convert
        temp_output_path = AudioConversionService.trim_audio(input_path, segments_list)
        output_path = temp_output_path
        
        # Get output file size
        output_file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type=target_ext,
            output_file_size=output_file_size
        )

        # Final rename
        target_path = os.path.join(settings.output_dir, final_filename)
        if os.path.abspath(output_path) != os.path.abspath(target_path):
             if os.path.exists(target_path): os.remove(target_path)
             shutil.move(output_path, target_path)

        success = True
        return ConversionResponse(
            success=True,
            message="Audio trimmed successfully",
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


# 8. Audio to Text
@router.post("/audio-to-text", response_model=ConversionResponse)
async def convert_audio_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    language: str = Form("en-US"),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert audio file to text using speech recognition."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "audio")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="audio-to-text",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="audio",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Perform audio to text conversion
        result = AudioConversionService.audio_to_text(input_path, language)
        
        # Determine output filename
        desired_name = (output_filename or input_filename).strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".txt",
        )
        output_path = output_path_final
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result["text"])
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="txt"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="Audio converted to text successfully",
            converted_data=result["text"],
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


@router.get("/download/{filename}")
async def download_file(filename: str, background_tasks: BackgroundTasks):
    """Download converted file and clean up."""
    file_path = os.path.join(settings.output_dir, filename)
    return FileService.create_cleanup_response(file_path, filename, background_tasks)

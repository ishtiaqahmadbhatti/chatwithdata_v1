import os
import inspect
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form, Query, Request, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional
from sqlalchemy.orm import Session
from app.app_models.schemas import ConversionResponse
from app.app_services.text_conversion_service import TextConversionService
from app.app_services.conversion_log_service import ConversionLogService
from app.app_core.database import get_db
from app.app_api.v1.dependencies import get_user_id
from app.app_core.exceptions import (
    FileProcessingError, 
    UnsupportedFileTypeError, 
    FileSizeExceededError,
    create_error_response
)
from app.app_services.file_service import FileService
from app.app_core.config import settings

router = APIRouter()


async def _handle_text_conversion(
    request: Request,
    db: Session,
    file: Optional[UploadFile] = None,
    file_key: Optional[str] = None,
    text: Optional[str] = None,
    tool_name: str = "text-conversion",
    output_filename: Optional[str] = None,
    output_extension: str = ".txt",
    **kwargs
) -> ConversionResponse:
    """Helper to handle generic text conversion."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        if text:
            # If text is provided directly, save it to a temp file
            temp_dir = settings.upload_dir
            if not os.path.exists(temp_dir): os.makedirs(temp_dir)
            fd, input_path = tempfile.mkstemp(suffix=".txt", dir=temp_dir)
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(text)
            input_filename = "direct_text.txt"
            input_size = len(text.encode('utf-8'))
        else:
            input_type = tool_name.split("-")[0] if "-" in tool_name else "document"
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
            default_extension=output_extension,
        )
        
        # Dispatch to correct service method
        method_name = tool_name.replace("-", "_")
        if hasattr(TextConversionService, method_name):
            method = getattr(TextConversionService, method_name)
            # Handle both sync and async methods
            if inspect.iscoroutinefunction(method):
                result_path = await method(input_path, output_filename=final_filename, **kwargs)
            else:
                result_path = method(input_path, output_filename=final_filename, **kwargs)
            output_path = result_path
        else:
            raise UnsupportedFileTypeError(f"Unsupported tool: {tool_name}")
            
        # Move to desired final path if different
        if os.path.exists(output_path) and os.path.abspath(output_path) != os.path.abspath(output_path_final):
            import shutil
            shutil.move(output_path, output_path_final)
            output_path = output_path_final

        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type=output_extension.lstrip(".")
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message=f"Operation {tool_name} completed successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/textconversiontools/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


@router.post("/word-to-text", response_model=ConversionResponse)
async def convert_word_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Word document to text."""
    return await _handle_text_conversion(request, db, file, file_key, tool_name="word-to-text", output_filename=output_filename)


@router.post("/powerpoint-to-text", response_model=ConversionResponse)
async def convert_powerpoint_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PowerPoint presentation to text."""
    return await _handle_text_conversion(request, db, file, file_key, tool_name="powerpoint-to-text", output_filename=output_filename)


@router.post("/pdf-to-text", response_model=ConversionResponse)
async def convert_pdf_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF document to text."""
    return await _handle_text_conversion(request, db, file, file_key, tool_name="pdf-to-text", output_filename=output_filename)


@router.post("/srt-to-text", response_model=ConversionResponse)
async def convert_srt_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT subtitle file to text."""
    return await _handle_text_conversion(request, db, file, file_key, tool_name="srt-to-text", output_filename=output_filename)


@router.post("/vtt-to-text", response_model=ConversionResponse)
async def convert_vtt_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert VTT subtitle file to text."""
    return await _handle_text_conversion(request, db, file, file_key, tool_name="vtt-to-text", output_filename=output_filename)


@router.post("/text-to-speech", response_model=ConversionResponse)
async def convert_text_to_speech(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    text: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    language: str = Form("en"),
    voice: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert text or document to speech (MP3) with voice selection. Accepts direct text input."""
    # Validation: at least one of file, file_key, or text must be provided
    if not any([file, file_key, text]):
        raise HTTPException(status_code=400, detail="At least one of 'file', 'file_key', or 'text' must be provided.")

    return await _handle_text_conversion(
        request, db, file, file_key, text=text, tool_name="text-to-speech", 
        output_filename=output_filename, output_extension=".mp3", language=language, voice=voice
    )


@router.get("/voices")
async def get_available_voices():
    """Get list of popular neural voices with their aliases."""
    return {
        "success": True,
        "voices": TextConversionService.POPULAR_VOICES,
        "message": "Available voices retrieved successfully"
    }


@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported input formats."""
    try:
        formats = TextConversionService.get_supported_formats()
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


@router.get("/download/{filename}")
async def download_file(filename: str, background_tasks: BackgroundTasks):
    """Download converted file and clean up."""
    file_path = os.path.join(settings.output_dir, filename)
    return FileService.create_cleanup_response(file_path, filename, background_tasks)

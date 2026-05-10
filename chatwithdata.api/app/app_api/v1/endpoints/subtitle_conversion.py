import os
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form, Query, Request, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional
from sqlalchemy.orm import Session
from app.app_models.schemas import ConversionResponse
from app.app_services.subtitle_conversion_service import SubtitleConversionService
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
from app.app_services.s3_service import s3_service

router = APIRouter()


async def _handle_subtitle_conversion(
    request: Request,
    db: Session,
    file: Optional[UploadFile] = None,
    file_key: Optional[str] = None,
    output_format: str = "srt",
    tool_name: str = "subtitle-conversion",
    output_filename: Optional[str] = None,
    **kwargs
) -> ConversionResponse:
    """Helper to handle generic subtitle conversion."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_type = tool_name.split("-")[0] if "-" in tool_name else "subtitle"
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
        if hasattr(SubtitleConversionService, method_name):
            method = getattr(SubtitleConversionService, method_name)
            
            # Subtitle service methods take different arguments
            if tool_name == "translate-srt":
                result_path = method(
                    input_path, 
                    kwargs.get("target_language", "en"), 
                    kwargs.get("source_language", "auto"), 
                    output_filename=final_filename
                )
            elif tool_name == "srt-to-excel":
                result_path = method(input_path, kwargs.get("format_type", "xlsx"), output_filename=final_filename)
            else:
                result_path = method(input_path, output_filename=final_filename)
                
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
            output_file_type=output_format.lower()
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message=f"File converted to {output_format.upper()} successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/subtitleconversiontools/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))

@router.post("/translate-srt", response_model=ConversionResponse)
async def translate_srt(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    target_language: str = Form("en"),
    source_language: str = Form("auto"),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Translate SRT subtitle file using AI translation."""
    return await _handle_subtitle_conversion(
        request, db, file, file_key, "srt", "translate-srt", output_filename,
        target_language=target_language, source_language=source_language
    )

@router.post("/srt-to-csv", response_model=ConversionResponse)
async def convert_srt_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT subtitle file to CSV format."""
    return await _handle_subtitle_conversion(
        request, db, file, file_key, "csv", "srt-to-csv", output_filename
    )

@router.post("/srt-to-excel", response_model=ConversionResponse)
async def convert_srt_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    format_type: str = Form("xlsx"),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT subtitle file to Excel format."""
    return await _handle_subtitle_conversion(
        request, db, file, file_key, format_type, "srt-to-excel", output_filename, format_type=format_type
    )

@router.post("/srt-to-text", response_model=ConversionResponse)
async def convert_srt_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT subtitle file to plain text."""
    return await _handle_subtitle_conversion(
        request, db, file, file_key, "txt", "srt-to-text", output_filename
    )

@router.post("/srt-to-vtt", response_model=ConversionResponse)
async def convert_srt_to_vtt(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT subtitle file to VTT format."""
    return await _handle_subtitle_conversion(
        request, db, file, file_key, "vtt", "srt-to-vtt", output_filename
    )

@router.post("/vtt-to-text", response_model=ConversionResponse)
async def convert_vtt_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert VTT subtitle file to plain text."""
    return await _handle_subtitle_conversion(
        request, db, file, file_key, "txt", "vtt-to-text", output_filename
    )

@router.post("/vtt-to-srt", response_model=ConversionResponse)
async def convert_vtt_to_srt(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert VTT subtitle file to SRT format."""
    return await _handle_subtitle_conversion(
        request, db, file, file_key, "srt", "vtt-to-srt", output_filename
    )

@router.post("/csv-to-srt", response_model=ConversionResponse)
async def convert_csv_to_srt(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert CSV subtitle file to SRT format."""
    return await _handle_subtitle_conversion(
        request, db, file, file_key, "srt", "csv-to-srt", output_filename
    )

@router.post("/excel-to-srt", response_model=ConversionResponse)
async def convert_excel_to_srt(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Excel subtitle file to SRT format."""
    return await _handle_subtitle_conversion(
        request, db, file, file_key, "srt", "excel-to-srt", output_filename
    )


@router.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported translation languages."""
    try:
        languages = SubtitleConversionService.get_supported_languages()
        return {
            "success": True,
            "languages": languages,
            "message": "Supported languages retrieved successfully"
        }
    except Exception as e:
        raise create_error_response(
            error_type="InternalServerError",
            message="Failed to retrieve supported languages",
            details={"error": str(e)},
            status_code=500
        )


@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported input and output formats."""
    try:
        formats = SubtitleConversionService.get_supported_formats()
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

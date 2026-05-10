
import os
import shutil
import logging
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form, Query, Request, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.app_models.schemas import ConversionResponse
from app.app_services.ocr_conversion_service import OCRConversionService
from app.app_services.conversion_log_service import ConversionLogService
from app.app_services.file_service import FileService
from app.app_core.config import settings
from app.app_core.database import get_db
from app.app_api.v1.dependencies import get_user_id
from app.app_core.exceptions import (
    FileProcessingError, 
    UnsupportedFileTypeError, 
    FileSizeExceededError,
    create_error_response
)

router = APIRouter()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _determine_output_filename(
    user_filename: Optional[str],
    input_file: Optional[UploadFile],
    default_base: str,
    extension: str
) -> str:
    """
    Determine the output filename based on user input, uploaded file, or default.
    Ensures correct extension.
    """
    # Ensure extension starts with dot
    if not extension.startswith('.'):
        extension = f'.{extension}'

    if user_filename and user_filename.strip() and user_filename.lower() != "string":
        # Use user provided filename
        filename = user_filename.strip()
        if not filename.lower().endswith(extension.lower()):
            filename += extension
        return filename
    else:
        # Fallback to input file name or default
        base_name = default_base
        if input_file and input_file.filename:
            # Strip input extension
            base_name = os.path.splitext(input_file.filename)[0]
        
        return f"{base_name}{extension}"

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

async def _handle_ocr_conversion(
    request: Request,
    db: Session,
    file: Optional[UploadFile] = None,
    file_key: Optional[str] = None,
    language: str = "eng",
    ocr_engine: str = "tesseract",
    tool_name: str = "ocr-conversion",
    output_filename: Optional[str] = None,
    output_format: str = "txt"
) -> ConversionResponse:
    """Helper to handle generic OCR conversion."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_type = tool_name.split("-")[0] if "-" in tool_name else "image"
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
        
        extracted_text = None
        
        # Dispatch based on tool_name
        if tool_name in ["png-to-text", "jpg-to-text"]:
            extracted_text = OCRConversionService.extract_text_from_image(input_path, language, ocr_engine)
            output_path = output_path_final
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(extracted_text)
        elif tool_name in ["png-to-pdf", "jpg-to-pdf"]:
            service_output_path = OCRConversionService.image_to_pdf_with_ocr(input_path, language, ocr_engine)
            output_path = service_output_path
        elif tool_name == "pdf-to-text":
            extracted_text = OCRConversionService.pdf_to_text_with_ocr(input_path, language, ocr_engine)
            output_path = output_path_final
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(extracted_text)
        elif tool_name == "pdf-image-to-pdf-text":
            service_output_path = OCRConversionService.pdf_image_to_pdf_text(input_path, language, ocr_engine)
            output_path = service_output_path
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
            extracted_text=extracted_text,
            output_filename=final_filename,
            download_url=f"/api/v1/ocrconversiontools/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


@router.post("/png-to-text", response_model=ConversionResponse)
async def convert_png_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    language: str = Form("eng"),
    ocr_engine: str = Form("tesseract"),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PNG image to text using OCR."""
    return await _handle_ocr_conversion(request, db, file, file_key, language, ocr_engine, "png-to-text", filename, "txt")


@router.post("/jpg-to-text", response_model=ConversionResponse)
async def convert_jpg_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    language: str = Form("eng"),
    ocr_engine: str = Form("tesseract"),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert JPG image to text using OCR."""
    return await _handle_ocr_conversion(request, db, file, file_key, language, ocr_engine, "jpg-to-text", filename, "txt")


@router.post("/png-to-pdf", response_model=ConversionResponse)
async def convert_png_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    language: str = Form("eng"),
    ocr_engine: str = Form("tesseract"),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PNG image to PDF with OCR text layer."""
    return await _handle_ocr_conversion(request, db, file, file_key, language, ocr_engine, "png-to-pdf", filename, "pdf")


@router.post("/jpg-to-pdf", response_model=ConversionResponse)
async def convert_jpg_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    language: str = Form("eng"),
    ocr_engine: str = Form("tesseract"),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert JPG image to PDF with OCR text layer."""
    return await _handle_ocr_conversion(request, db, file, file_key, language, ocr_engine, "jpg-to-pdf", filename, "pdf")


@router.post("/pdf-to-text", response_model=ConversionResponse)
async def convert_pdf_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    language: str = Form("eng"),
    ocr_engine: str = Form("tesseract"),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to text using OCR."""
    return await _handle_ocr_conversion(request, db, file, file_key, language, ocr_engine, "pdf-to-text", filename, "txt")


@router.post("/pdf-image-to-pdf-text", response_model=ConversionResponse)
async def convert_pdf_image_to_pdf_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    language: str = Form("eng"),
    ocr_engine: str = Form("tesseract"),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF with images to PDF with searchable text."""
    return await _handle_ocr_conversion(request, db, file, file_key, language, ocr_engine, "pdf-image-to-pdf-text", filename, "pdf")


@router.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported OCR languages."""
    try:
        languages = OCRConversionService.get_supported_languages()
        return {
            "success": True,
            "languages": languages,
            "message": "Supported languages retrieved successfully"
        }
    except Exception as e:
        raise create_error_response("InternalServerError", "Failed to retrieve supported languages", 500, {"error": str(e)})


@router.get("/supported-ocr-engines")
async def get_supported_ocr_engines():
    """Get list of supported OCR engines."""
    try:
        engines = OCRConversionService.get_supported_ocr_engines()
        return {
            "success": True,
            "engines": engines,
            "message": "Supported OCR engines retrieved successfully"
        }
    except Exception as e:
        raise create_error_response("InternalServerError", "Failed to retrieve supported OCR engines", 500, {"error": str(e)})


@router.get("/download/{filename}")
async def download_file(filename: str, background_tasks: BackgroundTasks):
    """Download converted file and clean up."""
    file_path = os.path.join(settings.output_dir, filename)
    return FileService.create_cleanup_response(file_path, filename, background_tasks)

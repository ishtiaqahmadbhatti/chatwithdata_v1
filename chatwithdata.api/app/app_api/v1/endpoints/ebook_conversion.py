import os
import shutil
import logging
from typing import Optional, List
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form, Query, Request, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.app_models.schemas import ConversionResponse
from app.app_services.ebook_conversion_service import EBookConversionService
from app.app_services.conversion_log_service import ConversionLogService
from app.app_core.database import get_db
from app.app_api.v1.dependencies import get_user_id
from app.app_core.config import settings
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
    return f"/api/v1/ebookconversiontools/download/{filename}"


async def _handle_ebook_conversion(
    request: Request,
    db: Session,
    file: Optional[UploadFile] = None,
    file_key: Optional[str] = None,
    output_format: str = "pdf",
    tool_name: str = "ebook-conversion",
    output_filename: Optional[str] = None,
    **kwargs
) -> ConversionResponse:
    """Helper to handle generic ebook conversion."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "document")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type=tool_name,
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type=input_filename.split('.')[-1].lower() if '.' in input_filename else "document",
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
        if hasattr(EBookConversionService, method_name):
            method = getattr(EBookConversionService, method_name)
            # Some methods might need title/author
            if "title" in kwargs and "author" in kwargs:
                 temp_output_path = method(input_path, kwargs["title"], kwargs["author"])
            else:
                 temp_output_path = method(input_path)
        else:
            # Fallback for formats not explicitly mapped in service method naming
             temp_output_path = EBookConversionService.convert_ebook(input_path, output_format.upper())
        
        output_path = temp_output_path
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type=output_format.lower()
        )
        
        # Final rename
        target_path = os.path.join(settings.output_dir, final_filename)
        if os.path.abspath(output_path) != os.path.abspath(target_path):
             if os.path.exists(target_path): os.remove(target_path)
             shutil.move(output_path, target_path)

        success = True
        return ConversionResponse(
            success=True,
            message=f"Ebook converted to {output_format.upper()} successfully",
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


@router.post("/markdown-to-epub", response_model=ConversionResponse)
async def convert_markdown_to_epub(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    title: str = Form("Converted Book"),
    author: str = Form("Unknown"),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Markdown file to EPUB format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "epub", "markdown-to-epub", output_filename, title=title, author=author)


@router.post("/epub-to-mobi", response_model=ConversionResponse)
async def convert_epub_to_mobi(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert EPUB file to MOBI format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "mobi", "epub-to-mobi", output_filename)


@router.post("/epub-to-azw", response_model=ConversionResponse)
async def convert_epub_to_azw(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert EPUB file to AZW format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "azw", "epub-to-azw", output_filename)


@router.post("/mobi-to-epub", response_model=ConversionResponse)
async def convert_mobi_to_epub(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert MOBI file to EPUB format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "epub", "mobi-to-epub", output_filename)


@router.post("/mobi-to-azw", response_model=ConversionResponse)
async def convert_mobi_to_azw(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert MOBI file to AZW format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "azw", "mobi-to-azw", output_filename)


@router.post("/azw-to-epub", response_model=ConversionResponse)
async def convert_azw_to_epub(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert AZW file to EPUB format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "epub", "azw-to-epub", output_filename)


@router.post("/azw-to-mobi", response_model=ConversionResponse)
async def convert_azw_to_mobi(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert AZW file to MOBI format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "mobi", "azw-to-mobi", output_filename)


@router.post("/epub-to-pdf", response_model=ConversionResponse)
async def convert_epub_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert EPUB file to PDF format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "pdf", "epub-to-pdf", output_filename)


@router.post("/mobi-to-pdf", response_model=ConversionResponse)
async def convert_mobi_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert MOBI file to PDF format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "pdf", "mobi-to-pdf", output_filename)


@router.post("/azw-to-pdf", response_model=ConversionResponse)
async def convert_azw_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert AZW file to PDF format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "pdf", "azw-to-pdf", output_filename)


@router.post("/azw3-to-pdf", response_model=ConversionResponse)
async def convert_azw3_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert AZW3 file to PDF format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "pdf", "azw3-to-pdf", output_filename)


@router.post("/fb2-to-pdf", response_model=ConversionResponse)
async def convert_fb2_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert FB2 file to PDF format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "pdf", "fb2-to-pdf", output_filename)


@router.post("/fbz-to-pdf", response_model=ConversionResponse)
async def convert_fbz_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert FBZ file to PDF format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "pdf", "fbz-to-pdf", output_filename)


@router.post("/pdf-to-epub", response_model=ConversionResponse)
async def convert_pdf_to_epub(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF file to EPUB format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "epub", "pdf-to-epub", output_filename)


@router.post("/pdf-to-mobi", response_model=ConversionResponse)
async def convert_pdf_to_mobi(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF file to MOBI format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "mobi", "pdf-to-mobi", output_filename)


@router.post("/pdf-to-azw", response_model=ConversionResponse)
async def convert_pdf_to_azw(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF file to AZW format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "azw", "pdf-to-azw", output_filename)


@router.post("/pdf-to-azw3", response_model=ConversionResponse)
async def convert_pdf_to_azw3(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF file to AZW3 format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "azw3", "pdf-to-azw3", output_filename)


@router.post("/pdf-to-fb2", response_model=ConversionResponse)
async def convert_pdf_to_fb2(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF file to FB2 format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "fb2", "pdf-to-fb2", output_filename)


@router.post("/pdf-to-fbz", response_model=ConversionResponse)
async def convert_pdf_to_fbz(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF file to FBZ format."""
    return await _handle_ebook_conversion(request, db, file, file_key, "fbz", "pdf-to-fbz", output_filename)


@router.get("/download/{filename}")
async def download_file(filename: str, background_tasks: BackgroundTasks):
    """Download converted file and clean up."""
    file_path = os.path.join(settings.output_dir, filename)
    return FileService.create_cleanup_response(file_path, filename, background_tasks)

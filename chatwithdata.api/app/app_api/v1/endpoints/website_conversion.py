"""
Website Conversion API Endpoints

This module provides API endpoints for various website and HTML conversion operations.
"""

import json
import logging
import os
import tempfile
from typing import Optional, Union
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session

from app.app_services.website_conversion_service_simple import WebsiteConversionService
from app.app_services.conversion_log_service import ConversionLogService
from app.app_services.file_service import FileService
from app.app_core.database import get_db
from app.app_api.v1.dependencies import get_user_id
from app.app_core.exceptions import (
    FileProcessingError, 
    UnsupportedFileTypeError, 
    FileSizeExceededError,
    create_error_response
)
from app.app_core.config import settings
from app.app_models.schemas import ConversionResponse

logger = logging.getLogger(__name__)

router = APIRouter()


# HTML to PDF
# HTML to PDF
async def _handle_website_conversion(
    request: Request,
    db: Session,
    file: Optional[UploadFile] = None,
    file_key: Optional[str] = None,
    url: Optional[str] = None,
    content: Optional[str] = None,
    tool_name: str = "website-conversion",
    output_format: str = "pdf",
    output_filename: Optional[str] = None,
    **kwargs
) -> ConversionResponse:
    """Helper to handle generic website/html conversion."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_filename = "content"
        input_size = 0
        input_type = "html"
        
        if (file and file.filename) or file_key:
            validation_type = "document"
            if "powerpoint" in tool_name or "excel" in tool_name or "word" in tool_name:
                validation_type = "office"
            elif tool_name.startswith("pdf-"):
                validation_type = "pdf"
            elif "markdown" in tool_name:
                validation_type = "markdown"
            elif "html" in tool_name or "website" in tool_name:
                validation_type = "document"
                
            input_path, input_filename, input_size = FileService.get_file_input(file, file_key, validation_type)
            input_type = input_filename.split('.')[-1].lower() if '.' in input_filename else "document"
        elif url:
            input_filename = url
            input_size = 0
            input_type = "url"
        elif content:
            input_filename = "raw_content"
            input_size = len(content)
            input_type = tool_name.split("-")[0] if "-" in tool_name else "html"
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type=tool_name,
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type=input_type,
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
        if tool_name == "html-to-pdf":
            if input_path:
                result_path = WebsiteConversionService.convert_html_file_to_pdf(input_path, final_filename)
            else:
                result_path = WebsiteConversionService.html_to_pdf(content, kwargs.get("css_content"), final_filename)
        elif tool_name == "website-to-pdf":
            result_path = WebsiteConversionService.website_to_pdf(url, final_filename)
        elif tool_name == "word-to-html":
            file_content = open(input_path, "rb").read() if input_path else b""
            result_path = WebsiteConversionService.word_to_html(file_content, input_filename, final_filename)
        elif tool_name == "powerpoint-to-html":
            file_content = open(input_path, "rb").read() if input_path else b""
            result_path = WebsiteConversionService.powerpoint_to_html(file_content, input_filename, final_filename)
        elif tool_name == "markdown-to-html":
            md_content = content or (open(input_path, "r", encoding="utf-8").read() if input_path else "")
            result_path = WebsiteConversionService.markdown_to_html(md_content, input_filename if input_path else None, final_filename)
        elif tool_name == "website-to-jpg":
            result_path = WebsiteConversionService.website_to_jpg(url, final_filename, kwargs.get("width", 1920), kwargs.get("height", 1080))
        elif tool_name == "html-to-jpg":
            html_content = content or (open(input_path, "r", encoding="utf-8").read() if input_path else "")
            result_path = WebsiteConversionService.html_to_jpg(html_content, input_filename if input_path else None, final_filename, kwargs.get("width", 1920), kwargs.get("height", 1080))
        elif tool_name == "website-to-png":
            result_path = WebsiteConversionService.website_to_png(url, final_filename, kwargs.get("width", 1920), kwargs.get("height", 1080))
        elif tool_name == "html-to-png":
            html_content = content or (open(input_path, "r", encoding="utf-8").read() if input_path else "")
            result_path = WebsiteConversionService.html_to_png(html_content, input_filename if input_path else None, final_filename, kwargs.get("width", 1920), kwargs.get("height", 1080))
        elif tool_name == "html-table-to-csv":
            html_content = content or (open(input_path, "r", encoding="utf-8").read() if input_path else "")
            result_path = WebsiteConversionService.html_table_to_csv(html_content, final_filename, input_filename if input_path else None)
        elif tool_name == "excel-to-html":
            file_content = open(input_path, "rb").read() if input_path else b""
            result_path = WebsiteConversionService.excel_to_html(file_content, input_filename, final_filename)
        elif tool_name == "pdf-to-html":
            file_content = open(input_path, "rb").read() if input_path else b""
            result_path = WebsiteConversionService.pdf_to_html(file_content, input_filename, final_filename)
        else:
            raise UnsupportedFileTypeError(f"Unsupported tool: {tool_name}")
            
        output_path = result_path
        
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
            message=f"Conversion to {output_format.upper()} successful",
            output_filename=final_filename,
            download_url=f"/api/v1/websiteconversiontools/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


@router.post("/html-to-pdf", response_model=ConversionResponse)
async def convert_html_to_pdf(
    request: Request,
    html_content: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    css_content: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert HTML content or file to PDF."""
    return await _handle_website_conversion(
        request, db, file, file_key, None, content or html_content, "html-to-pdf", "pdf", filename, css_content=css_content
    )


@router.post("/website-to-pdf", response_model=ConversionResponse)
async def convert_website_to_pdf(
    request: Request,
    url: str = Form(...),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Website URL to PDF."""
    return await _handle_website_conversion(
        request, db, None, None, url, None, "website-to-pdf", "pdf", filename
    )


@router.post("/word-to-html", response_model=ConversionResponse)
async def convert_word_to_html(
    request: Request,
    filename: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Word document to HTML."""
    return await _handle_website_conversion(
        request, db, file, file_key, None, None, "word-to-html", "html", filename
    )


@router.post("/powerpoint-to-html", response_model=ConversionResponse)
async def convert_powerpoint_to_html(
    request: Request,
    filename: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PowerPoint presentation to HTML."""
    return await _handle_website_conversion(
        request, db, file, file_key, None, None, "powerpoint-to-html", "html", filename
    )


@router.post("/markdown-to-html", response_model=ConversionResponse)
async def convert_markdown_to_html(
    request: Request,
    filename: Optional[str] = Form(None),
    markdown_content: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Markdown content or file to HTML."""
    return await _handle_website_conversion(
        request, db, file, file_key, None, content or markdown_content, "markdown-to-html", "html", filename
    )


@router.post("/website-to-jpg", response_model=ConversionResponse)
async def convert_website_to_jpg(
    request: Request,
    url: str = Form(...),
    filename: Optional[str] = Form(None),
    width: int = Form(1920),
    height: int = Form(1080),
    db: Session = Depends(get_db)
):
    """Convert website to JPG image."""
    return await _handle_website_conversion(
        request, db, None, None, url, None, "website-to-jpg", "jpg", filename, width=width, height=height
    )


@router.post("/html-to-jpg", response_model=ConversionResponse)
async def convert_html_to_jpg(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    html_content: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    width: int = Form(1920),
    height: int = Form(1080),
    db: Session = Depends(get_db)
):
    """Convert HTML content or file to JPG image."""
    return await _handle_website_conversion(
        request, db, file, file_key, None, content or html_content, "html-to-jpg", "jpg", filename, width=width, height=height
    )


@router.post("/website-to-png", response_model=ConversionResponse)
async def convert_website_to_png(
    request: Request,
    url: str = Form(...),
    filename: Optional[str] = Form(None),
    width: int = Form(1920),
    height: int = Form(1080),
    db: Session = Depends(get_db)
):
    """Convert website to PNG image."""
    return await _handle_website_conversion(
        request, db, None, None, url, None, "website-to-png", "png", filename, width=width, height=height
    )


@router.post("/html-to-png", response_model=ConversionResponse)
async def convert_html_to_png(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    html_content: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    width: int = Form(1920),
    height: int = Form(1080),
    db: Session = Depends(get_db)
):
    """Convert HTML content or file to PNG image."""
    return await _handle_website_conversion(
        request, db, file, file_key, None, content or html_content, "html-to-png", "png", filename, width=width, height=height
    )


@router.post("/html-table-to-csv", response_model=ConversionResponse)
async def convert_html_table_to_csv(
    request: Request,
    html_content: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert HTML table to CSV."""
    return await _handle_website_conversion(
        request, db, file, file_key, None, content or html_content, "html-table-to-csv", "csv", filename
    )


@router.post("/excel-to-html", response_model=ConversionResponse)
async def convert_excel_to_html(
    request: Request,
    filename: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Excel file to HTML."""
    return await _handle_website_conversion(
        request, db, file, file_key, None, None, "excel-to-html", "html", filename
    )


@router.post("/pdf-to-html", response_model=ConversionResponse)
async def convert_pdf_to_html(
    request: Request,
    filename: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to HTML."""
    return await _handle_website_conversion(
        request, db, file, file_key, None, None, "pdf-to-html", "html", filename
    )


# Download endpoint for generated files
@router.get("/download/{filename}")
async def download_file(filename: str, background_tasks: BackgroundTasks):
    """Download a generated file and clean up."""
    file_path = os.path.join(settings.output_dir, filename)
    return FileService.create_cleanup_response(file_path, filename, background_tasks)

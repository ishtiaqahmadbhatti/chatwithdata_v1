"""
Image Conversion API Endpoints

This module provides API endpoints for various Image conversion operations.
"""

import os
import shutil
import logging
import json
from typing import Optional, List
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form, Query, Request, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.app_models.schemas import ConversionResponse
from app.app_services.image_conversion_service import ImageConversionService
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


def _build_download_url(filename: str) -> str:
    """Build consistent download url for generated files."""
    return f"/api/v1/imageconversiontools/download/{filename}"


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


async def _handle_image_conversion(
    request: Request,
    db: Session,
    file: Optional[UploadFile] = None,
    file_key: Optional[str] = None,
    output_format: str = "PNG",
    tool_name: str = "image-conversion",
    output_filename: Optional[str] = None,
    quality: int = 95
) -> ConversionResponse:
    """Helper to handle generic image conversion."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "image")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type=tool_name,
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="image",
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
        
        # Convert
        temp_output_path = ImageConversionService.convert_image_format(
            input_path, output_format.upper(), quality
        )
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
            message=f"Image converted to {output_format.upper()} successfully",
            output_filename=final_filename,
            download_url=_build_download_url(final_filename)
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        logger.error(f"Image conversion error in _handle_image_conversion: {str(e)}")
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else output_path)


async def _handle_json_conversion(
    request: Request,
    db: Session,
    file: Optional[UploadFile] = None,
    file_key: Optional[str] = None,
    tool_name: str = "image-to-json",
    output_filename: Optional[str] = None,
    include_metadata: bool = True
) -> ConversionResponse:
    """Helper to handle image to json conversion."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "image")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type=tool_name,
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="image",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (output_filename or input_filename).strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".json",
        )
        
        # Convert
        temp_output_path = ImageConversionService.image_to_json(input_path)
        output_path = temp_output_path
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="json"
        )
        
        # Final rename
        target_path = os.path.join(settings.output_dir, final_filename)
        if os.path.abspath(output_path) != os.path.abspath(target_path):
             if os.path.exists(target_path): os.remove(target_path)
             shutil.move(output_path, target_path)

        success = True
        return ConversionResponse(
            success=True,
            message="Image converted to JSON successfully",
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


async def _handle_image_to_pdf(
    request: Request,
    db: Session,
    file: Optional[UploadFile] = None,
    file_key: Optional[str] = None,
    tool_name: str = "image-to-pdf",
    output_filename: Optional[str] = None,
    page_size: str = "A4"
) -> ConversionResponse:
    """Helper to handle image to pdf conversion."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "image")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type=tool_name,
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="image",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (output_filename or input_filename).strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )
        
        # Convert
        temp_output_path = ImageConversionService.image_to_pdf(input_path, page_size)
        output_path = temp_output_path
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        # Final rename
        target_path = os.path.join(settings.output_dir, final_filename)
        if os.path.abspath(output_path) != os.path.abspath(target_path):
             if os.path.exists(target_path): os.remove(target_path)
             shutil.move(output_path, target_path)

        success = True
        return ConversionResponse(
            success=True,
            message="Image converted to PDF successfully",
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


async def _handle_website_conversion(
    request: Request,
    db: Session,
    url: str,
    output_format: str,
    tool_name: str,
    output_filename: Optional[str],
    width: int,
    height: int
) -> ConversionResponse:
    """Helper to handle website conversion."""
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type=tool_name,
            input_filename=url,
            input_file_size=0, 
            input_file_type="url",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        default_base = f"website_{url.replace('://', '_').replace('/', '_')}"[:50]
        desired_name = (output_filename or default_base).strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=f".{output_format.lower()}",
        )
        
        # Convert
        temp_output_path = ImageConversionService.website_to_image(
            url, output_format.upper(), width, height
        )
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
            message=f"Website converted to {output_format} successfully",
            output_filename=final_filename,
            download_url=_build_download_url(final_filename)
        )
        
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        if not success and output_path:
             FileService.cleanup_files(None, output_path)


async def _handle_html_conversion(
    request: Request,
    db: Session,
    html_content: str,
    output_format: str,
    tool_name: str,
    output_filename: Optional[str],
    width: int,
    height: int
) -> ConversionResponse:
    """Helper to handle HTML conversion."""
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type=tool_name,
            input_filename="HTML Content",
            input_file_size=len(html_content),
            input_file_type="html",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine output filename
        desired_name = (output_filename or "html_content").strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=f".{output_format.lower()}",
        )
        
        # Convert
        temp_output_path = ImageConversionService.html_to_image(
            html_content, output_format.upper(), width, height
        )
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
            message=f"HTML converted to {output_format} successfully",
            output_filename=final_filename,
            download_url=_build_download_url(final_filename)
        )
        
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        if not success and output_path:
             FileService.cleanup_files(None, output_path)


async def _handle_pdf_conversion(
    request: Request,
    db: Session,
    file: Optional[UploadFile] = None,
    file_key: Optional[str] = None,
    output_format: str = "PNG",
    tool_name: str = "pdf-to-image",
    output_filename: Optional[str] = None,
    dpi: int = 300,
    page_number: int = 1
) -> ConversionResponse:
    """Helper to handle PDF conversion."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "pdf")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type=tool_name,
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Base name handling for folder
        import re
        base_name, _ = os.path.splitext(input_filename or "pdf_images")
        desired_base = (output_filename or base_name).strip()
        sanitized_base = re.sub(r"[^A-Za-z0-9._-]+", "_", desired_base).strip("._")
        if not sanitized_base:
            sanitized_base = "pdf_images"

        output_root = settings.output_dir
        os.makedirs(output_root, exist_ok=True)

        folder_name = sanitized_base
        folder_path = os.path.join(output_root, folder_name)
        counter = 1
        while os.path.exists(folder_path):
            folder_name = f"{sanitized_base}_{counter}"
            folder_path = os.path.join(output_root, folder_name)
            counter += 1

        os.makedirs(folder_path, exist_ok=True)

        # Get total pages and convert using fitz (PyMuPDF) - faster and no poppler dependency
        import fitz
        from PIL import Image
        try:
            with fitz.open(input_path) as doc:
                total_pages = len(doc)
                
                renamed_files = []
                for i in range(total_pages):
                    page = doc.load_page(i)
                    
                    # Higher DPI for better quality
                    zoom = dpi / 72  # 72 is the default PDF DPI
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    
                    new_name = f"{folder_name}_page_{i+1}.{output_format.lower()}"
                    new_path = os.path.join(folder_path, new_name)
                    
                    format_lower = output_format.lower()
                    if format_lower in {"jpg", "jpeg"}:
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        img.save(new_path, "JPEG", quality=95)
                    elif format_lower in {"tiff", "tif"}:
                        mode = "RGBA" if pix.alpha else "RGB"
                        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                        img.save(new_path, "TIFF")
                    elif format_lower == "svg":
                        svg_data = page.get_svg_image()
                        with open(new_path, "w", encoding="utf-8") as f_svg:
                            f_svg.write(svg_data)
                    else:
                        # Default to PNG or other pixmap-supported formats
                        pix.save(new_path)
                    
                    renamed_files.append(new_path)
        except Exception as e:
            logger.error(f"PDF conversion error in image_conversion: {str(e)}")
            raise FileProcessingError(f"PDF conversion failed: {str(e)}")

        # Zip the folder
        zip_base = os.path.join(output_root, folder_name)
        zip_path = shutil.make_archive(zip_base, 'zip', folder_path)
        zip_filename = os.path.basename(zip_path)
        shutil.rmtree(folder_path, ignore_errors=True)
        
        # Set output_path for cleanup in finally block
        output_path = zip_path

        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=zip_filename,
            output_file_type="zip"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message=f"PDF converted to {len(renamed_files)} {output_format} images successfully",
            output_filename=zip_filename,
            download_url=_build_download_url(zip_filename)
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else output_path)


async def _handle_ai_conversion(
    request: Request,
    db: Session,
    file: Optional[UploadFile] = None,
    file_key: Optional[str] = None,
    tool_name: str = "ai-to-svg",
    output_filename: Optional[str] = None
) -> ConversionResponse:
    """Helper for AI conversion."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "ai")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type=tool_name,
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="ai",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (output_filename or input_filename).strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".svg",
        )
        
        # Convert
        temp_output_path = ImageConversionService.ai_to_svg(input_path)
        output_path = temp_output_path
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="svg"
        )
        
        # Final rename
        target_path = os.path.join(settings.output_dir, final_filename)
        if os.path.abspath(output_path) != os.path.abspath(target_path):
             if os.path.exists(target_path): os.remove(target_path)
             shutil.move(output_path, target_path)

        success = True
        return ConversionResponse(
            success=True,
            message="AI converted to SVG successfully",
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


# ---------------------------------------------------------------------------
# Core Endpoints
# ---------------------------------------------------------------------------

@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported inputs/outputs."""
    return {
        "success": True, 
        "formats": ImageConversionService.get_supported_formats(),
        "message": "Supported formats retrieved successfully"
    }

@router.get("/download/{filename}")
async def download_file(filename: str, background_tasks: BackgroundTasks):
    """Download converted file and clean up."""
    file_path = os.path.join(settings.output_dir, filename)
    return FileService.create_cleanup_response(file_path, filename, background_tasks)

# ---------------------------------------------------------------------------
# Specific Format endpoints
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 1. AI: Convert PNG to JSON
# ---------------------------------------------------------------------------
@router.post("/ai-png-to-json", response_model=ConversionResponse)
async def convert_ai_png_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """AI: Convert PNG to JSON."""
    return await _handle_json_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        tool_name="ai-png-to-json", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 2. AI: Convert JPG to JSON
# ---------------------------------------------------------------------------
@router.post("/ai-jpg-to-json", response_model=ConversionResponse)
async def convert_ai_jpg_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """AI: Convert JPG to JSON."""
    return await _handle_json_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        tool_name="ai-jpg-to-json", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 3. Convert JPG to PDF
# ---------------------------------------------------------------------------
@router.post("/jpg-to-pdf", response_model=ConversionResponse)
async def convert_jpg_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert JPG to PDF."""
    return await _handle_image_to_pdf(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        tool_name="jpg-to-pdf", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 4. Convert PNG to PDF
# ---------------------------------------------------------------------------
@router.post("/png-to-pdf", response_model=ConversionResponse)
async def convert_png_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PNG to PDF."""
    return await _handle_image_to_pdf(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        tool_name="png-to-pdf", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 5. Convert Website to JPG
# ---------------------------------------------------------------------------
@router.post("/website-to-jpg", response_model=ConversionResponse)
async def convert_website_to_jpg(
    request: Request,
    url: str = Form(...),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Website to JPG."""
    return await _handle_website_conversion(
        request=request, 
        db=db, 
        url=url, 
        output_format="JPG", 
        tool_name="website-to-jpg", 
        output_filename=output_filename, 
        width=1920, 
        height=1080
    )

# ---------------------------------------------------------------------------
# 6. Convert HTML to JPG
# ---------------------------------------------------------------------------
@router.post("/html-to-jpg", response_model=ConversionResponse)
async def convert_html_to_jpg(
    request: Request,
    html_content: str = Form(...),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert HTML to JPG."""
    return await _handle_html_conversion(
        request=request, 
        db=db, 
        html_content=html_content, 
        output_format="JPG", 
        tool_name="html-to-jpg", 
        output_filename=output_filename, 
        width=1920, 
        height=1080
    )

# ---------------------------------------------------------------------------
# 7. Convert Website to PNG
# ---------------------------------------------------------------------------
@router.post("/website-to-png", response_model=ConversionResponse)
async def convert_website_to_png(
    request: Request,
    url: str = Form(...),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Website to PNG."""
    return await _handle_website_conversion(
        request=request, 
        db=db, 
        url=url, 
        output_format="PNG", 
        tool_name="website-to-png", 
        output_filename=output_filename, 
        width=1920, 
        height=1080
    )

# ---------------------------------------------------------------------------
# 8. Convert HTML to PNG
# ---------------------------------------------------------------------------
@router.post("/html-to-png", response_model=ConversionResponse)
async def convert_html_to_png(
    request: Request,
    html_content: str = Form(...),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert HTML to PNG."""
    return await _handle_html_conversion(
        request=request, 
        db=db, 
        html_content=html_content, 
        output_format="PNG", 
        tool_name="html-to-png", 
        output_filename=output_filename, 
        width=1920, 
        height=1080
    )

# ---------------------------------------------------------------------------
# 9. Convert PDF to JPG
# ---------------------------------------------------------------------------
@router.post("/pdf-to-jpg", response_model=ConversionResponse)
async def convert_pdf_to_jpg(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to JPG."""
    return await _handle_pdf_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="JPG", 
        tool_name="pdf-to-jpg", 
        output_filename=output_filename, 
        dpi=300, 
        page_number=1
    )

# ---------------------------------------------------------------------------
# 10. Convert PDF to PNG
# ---------------------------------------------------------------------------
@router.post("/pdf-to-png", response_model=ConversionResponse)
async def convert_pdf_to_png(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to PNG."""
    return await _handle_pdf_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="PNG", 
        tool_name="pdf-to-png", 
        output_filename=output_filename, 
        dpi=300, 
        page_number=1
    )

# ---------------------------------------------------------------------------
# 11. Convert PDF to TIFF
# ---------------------------------------------------------------------------
@router.post("/pdf-to-tiff", response_model=ConversionResponse)
async def convert_pdf_to_tiff_alias_v2(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to TIFF."""
    return await _handle_pdf_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="TIFF", 
        tool_name="pdf-to-tiff", 
        output_filename=output_filename, 
        dpi=300, 
        page_number=1
    )

# ---------------------------------------------------------------------------
# 12. Convert PDF to SVG
# ---------------------------------------------------------------------------
@router.post("/pdf-to-svg", response_model=ConversionResponse)
async def convert_pdf_to_svg_alias_v2(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to SVG."""
    return await _handle_pdf_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="SVG", 
        tool_name="pdf-to-svg", 
        output_filename=output_filename, 
        dpi=300, 
        page_number=1
    )

# ---------------------------------------------------------------------------
# 13. Convert AI to SVG
# ---------------------------------------------------------------------------
@router.post("/ai-to-svg", response_model=ConversionResponse)
async def convert_ai_to_svg_alias_v2(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert AI to SVG."""
    return await _handle_ai_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        tool_name="ai-to-svg", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 14. Convert PNG to SVG
# ---------------------------------------------------------------------------
@router.post("/png-to-svg", response_model=ConversionResponse)
async def convert_png_to_svg(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PNG to SVG."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="SVG", 
        tool_name="png-to-svg", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 15. Convert PNG to AVIF
# ---------------------------------------------------------------------------
@router.post("/png-to-avif", response_model=ConversionResponse)
async def convert_png_to_avif(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PNG to AVIF."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="AVIF", 
        tool_name="png-to-avif", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 16. Convert JPG to AVIF
# ---------------------------------------------------------------------------
@router.post("/jpg-to-avif", response_model=ConversionResponse)
async def convert_jpg_to_avif(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert JPG to AVIF."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="AVIF", 
        tool_name="jpg-to-avif", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 17. Convert WebP to AVIF
# ---------------------------------------------------------------------------
@router.post("/webp-to-avif", response_model=ConversionResponse)
async def convert_webp_to_avif(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert WebP to AVIF."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="AVIF", 
        tool_name="webp-to-avif", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 18. Convert AVIF to PNG
# ---------------------------------------------------------------------------
@router.post("/avif-to-png", response_model=ConversionResponse)
async def convert_avif_to_png(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert AVIF to PNG."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="PNG", 
        tool_name="avif-to-png", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 19. Convert AVIF to JPEG
# ---------------------------------------------------------------------------
@router.post("/avif-to-jpeg", response_model=ConversionResponse)
async def convert_avif_to_jpeg(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert AVIF to JPEG."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="JPEG", 
        tool_name="avif-to-jpeg", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 20. Convert AVIF to WebP
# ---------------------------------------------------------------------------
@router.post("/avif-to-webp", response_model=ConversionResponse)
async def convert_avif_to_webp(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert AVIF to WebP."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="WEBP", 
        tool_name="avif-to-webp", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 21. Convert PNG to WebP
# ---------------------------------------------------------------------------
@router.post("/png-to-webp", response_model=ConversionResponse)
async def convert_png_to_webp(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PNG to WebP."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="WEBP", 
        tool_name="png-to-webp", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 22. Convert JPG to WebP
# ---------------------------------------------------------------------------
@router.post("/jpg-to-webp", response_model=ConversionResponse)
async def convert_jpg_to_webp(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert JPG to WebP."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="WEBP", 
        tool_name="jpg-to-webp", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 23. Convert TIFF to WebP
# ---------------------------------------------------------------------------
@router.post("/tiff-to-webp", response_model=ConversionResponse)
async def convert_tiff_to_webp(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert TIFF to WebP."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="WEBP", 
        tool_name="tiff-to-webp", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 24. Convert GIF to WebP
# ---------------------------------------------------------------------------
@router.post("/gif-to-webp", response_model=ConversionResponse)
async def convert_gif_to_webp(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert GIF to WebP."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="WEBP", 
        tool_name="gif-to-webp", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 25. Convert WebP to PNG
# ---------------------------------------------------------------------------
@router.post("/webp-to-png", response_model=ConversionResponse)
async def convert_webp_to_png(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert WebP to PNG."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="PNG", 
        tool_name="webp-to-png", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 26. Convert WebP to JPEG
# ---------------------------------------------------------------------------
@router.post("/webp-to-jpeg", response_model=ConversionResponse)
async def convert_webp_to_jpeg(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert WebP to JPEG."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="JPEG", 
        tool_name="webp-to-jpeg", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 27. Convert WebP to TIFF
# ---------------------------------------------------------------------------
@router.post("/webp-to-tiff", response_model=ConversionResponse)
async def convert_webp_to_tiff(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert WebP to TIFF."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="TIFF", 
        tool_name="webp-to-tiff", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 28. Convert WebP to BMP
# ---------------------------------------------------------------------------
@router.post("/webp-to-bmp", response_model=ConversionResponse)
async def convert_webp_to_bmp(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert WebP to BMP."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="BMP", 
        tool_name="webp-to-bmp", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 29. Convert WebP to YUV
# ---------------------------------------------------------------------------
@router.post("/webp-to-yuv", response_model=ConversionResponse)
async def convert_webp_to_yuv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert WebP to YUV."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="YUV", 
        tool_name="webp-to-yuv", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 30. Convert WebP to PAM
# ---------------------------------------------------------------------------
@router.post("/webp-to-pam", response_model=ConversionResponse)
async def convert_webp_to_pam(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert WebP to PAM."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="PAM", 
        tool_name="webp-to-pam", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 31. Convert WebP to PGM
# ---------------------------------------------------------------------------
@router.post("/webp-to-pgm", response_model=ConversionResponse)
async def convert_webp_to_pgm(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert WebP to PGM."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="PGM", 
        tool_name="webp-to-pgm", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 32. Convert WebP to PPM
# ---------------------------------------------------------------------------
@router.post("/webp-to-ppm", response_model=ConversionResponse)
async def convert_webp_to_ppm(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert WebP to PPM."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="PPM", 
        tool_name="webp-to-ppm", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 33. Convert PNG to JPG
# ---------------------------------------------------------------------------
@router.post("/png-to-jpg", response_model=ConversionResponse)
async def convert_png_to_jpg(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PNG to JPG."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="JPG", 
        tool_name="png-to-jpg", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 34. Convert PNG to PGM
# ---------------------------------------------------------------------------
@router.post("/png-to-pgm", response_model=ConversionResponse)
async def convert_png_to_pgm(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PNG to PGM."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="PGM", 
        tool_name="png-to-pgm", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 35. Convert PNG to PPM
# ---------------------------------------------------------------------------
@router.post("/png-to-ppm", response_model=ConversionResponse)
async def convert_png_to_ppm(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PNG to PPM."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="PPM", 
        tool_name="png-to-ppm", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 36. Convert JPG to PNG
# ---------------------------------------------------------------------------
@router.post("/jpg-to-png", response_model=ConversionResponse)
async def convert_jpg_to_png(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert JPG to PNG."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="PNG", 
        tool_name="jpg-to-png", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 37. Convert JPEG to PGM
# ---------------------------------------------------------------------------
@router.post("/jpeg-to-pgm", response_model=ConversionResponse)
async def convert_jpeg_to_pgm(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert JPEG to PGM."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="PGM", 
        tool_name="jpeg-to-pgm", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 38. Convert JPEG to PPM
# ---------------------------------------------------------------------------
@router.post("/jpeg-to-ppm", response_model=ConversionResponse)
async def convert_jpeg_to_ppm(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert JPEG to PPM."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="PPM", 
        tool_name="jpeg-to-ppm", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 39. Convert HEIC to PNG
# ---------------------------------------------------------------------------
@router.post("/heic-to-png", response_model=ConversionResponse)
async def convert_heic_to_png(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert HEIC to PNG."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="PNG", 
        tool_name="heic-to-png", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 40. Convert HEIC to JPG
# ---------------------------------------------------------------------------
@router.post("/heic-to-jpg", response_model=ConversionResponse)
async def convert_heic_to_jpg(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert HEIC to JPG."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="JPG", 
        tool_name="heic-to-jpg", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 41. Convert SVG to PNG
# ---------------------------------------------------------------------------
@router.post("/svg-to-png", response_model=ConversionResponse)
async def convert_svg_to_png(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SVG to PNG."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="PNG", 
        tool_name="svg-to-png", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 42. Convert SVG to JPG
# ---------------------------------------------------------------------------
@router.post("/svg-to-jpg", response_model=ConversionResponse)
async def convert_svg_to_jpg(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SVG to JPG."""
    return await _handle_image_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="JPG", 
        tool_name="svg-to-jpg", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# 43. Remove EXIF Data
# ---------------------------------------------------------------------------
@router.post("/remove-exif", response_model=ConversionResponse)
async def remove_exif_data(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Remove EXIF data."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "image")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="remove-exif",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="image",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        ext = os.path.splitext(input_filename)[1] or ".jpg"
        desired_name = (output_filename or f"no_exif_{input_filename}").strip()
        output_path_final, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=ext,
        )
        
        # Convert
        temp_output_path = ImageConversionService.remove_exif_data(input_path)
        output_path = temp_output_path
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type=ext.lstrip('.') if ext else "image"
        )
        
        # Final rename
        target_path = os.path.join(settings.output_dir, final_filename)
        if os.path.abspath(output_path) != os.path.abspath(target_path):
             if os.path.exists(target_path): os.remove(target_path)
             shutil.move(output_path, target_path)

        success = True
        return ConversionResponse(
            success=True,
            message="EXIF data removed successfully",
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

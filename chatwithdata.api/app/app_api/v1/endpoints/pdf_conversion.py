import os
import re
from typing import List, Optional, Union, Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends, Request, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.app_core.database import get_db
from app.app_services.file_service import FileService
from app.app_services.pdf_conversion_service import PDFConversionService
from app.app_services.conversion_log_service import ConversionLogService
from app.app_api.v1.dependencies import get_current_user, get_user_id
from app.app_services.user_list_service import UserListService
from app.app_core.config import settings
from app.app_services.s3_service import s3_service
from app.app_core.exceptions import (
    FileProcessingError, 
    UnsupportedFileTypeError, 
    FileSizeExceededError,
    create_error_response
)

from PyPDF2 import PdfReader

router = APIRouter()


class PDFConversionResponse(BaseModel):
    """Response model for PDF conversion operations."""
    success: bool
    message: str
    output_filename: Optional[str] = None
    download_url: Optional[str] = None
    file_size_before: Optional[int] = None
    file_size_after: Optional[int] = None
    pages_processed: Optional[int] = None
    extracted_data: Optional[dict] = None


# Convert PDF to JSON
@router.post("/pdf-to-json", response_model=PDFConversionResponse)
async def convert_pdf_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to JSON with structured data extraction."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id from token or device_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "pdf")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="pdf-to-json",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine desired output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".json",
        )
        
        # Convert PDF to JSON
        result_path = PDFConversionService.pdf_to_json(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="json"
        )

        success = True
        return PDFConversionResponse(
            success=True,
            message="PDF converted to JSON successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert PDF to Markdown
@router.post("/pdf-to-markdown", response_model=PDFConversionResponse)
async def convert_pdf_to_markdown(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to Markdown format."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id from token or device_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "pdf")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="pdf-to-markdown",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine desired output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".md",
        )
        
        # Convert PDF to Markdown
        result_path = PDFConversionService.pdf_to_markdown(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="md"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PDF converted to Markdown successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert PDF to CSV
@router.post("/pdf-to-csv", response_model=PDFConversionResponse)
async def convert_pdf_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to CSV format (extract tabular data)."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id from token or device_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "pdf")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="pdf-to-csv",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine desired output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".csv",
        )

        # Convert PDF to CSV
        result_path = PDFConversionService.pdf_to_csv(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="csv"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PDF converted to CSV successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert PDF to Excel
@router.post("/pdf-to-excel", response_model=PDFConversionResponse)
async def convert_pdf_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to Excel format."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "pdf")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="pdf-to-excel",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine desired output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".xlsx",
        )
        
        # Convert PDF to Excel
        result_path = PDFConversionService.pdf_to_excel(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="xlsx"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PDF converted to Excel successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert HTML to PDF
@router.post("/html-to-pdf", response_model=PDFConversionResponse)
async def convert_html_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert HTML to PDF."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "document")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="html-to-pdf",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="html",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine desired output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )

        # Convert HTML to PDF
        result_path = PDFConversionService.html_to_pdf(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="HTML converted to PDF successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert Word to PDF
@router.post("/word-to-pdf", response_model=PDFConversionResponse)
async def convert_word_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Word document to PDF."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "office")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="word-to-pdf",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="docx",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine desired output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )
        result_path = PDFConversionService.word_to_pdf(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="Word document converted to PDF successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert PowerPoint to PDF
@router.post("/powerpoint-to-pdf", response_model=PDFConversionResponse)
async def convert_powerpoint_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PowerPoint to PDF."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "office")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="powerpoint-to-pdf",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pptx",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine desired output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )
        result_path = PDFConversionService.powerpoint_to_pdf(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PowerPoint converted to PDF successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert OXPS to PDF
@router.post("/oxps-to-pdf", response_model=PDFConversionResponse)
async def convert_oxps_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert OXPS to PDF."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "oxps")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="oxps-to-pdf",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="oxps",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine desired output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )
            
        # Convert OXPS to PDF
        result_path = PDFConversionService.oxps_to_pdf(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="OXPS converted to PDF successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert JPG to PDF
@router.post("/jpg-to-pdf", response_model=PDFConversionResponse)
async def convert_jpg_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert JPG image to PDF."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "jpg")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="jpg-to-pdf",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="jpg",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )
        
        # Convert JPG to PDF
        result_path = PDFConversionService.image_to_pdf(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="JPG image converted to PDF successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert PNG to PDF
@router.post("/png-to-pdf", response_model=PDFConversionResponse)
async def convert_png_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PNG image to PDF."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "png")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="png-to-pdf",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="png",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )
        
        # Convert PNG to PDF
        result_path = PDFConversionService.image_to_pdf(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PNG image converted to PDF successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert Markdown to PDF
@router.post("/markdown-to-pdf", response_model=PDFConversionResponse)
async def convert_markdown_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Markdown to PDF."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "markdown")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="markdown-to-pdf",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="md",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )
        
        # Convert Markdown to PDF
        result_path = PDFConversionService.markdown_to_pdf(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="Markdown converted to PDF successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert Excel to PDF
@router.post("/excel-to-pdf", response_model=PDFConversionResponse)
async def convert_excel_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Excel to PDF."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "office")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="excel-to-pdf",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="xlsx",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine desired output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )
            
        # Convert Excel to PDF
        result_path = PDFConversionService.excel_to_pdf(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="Excel converted to PDF successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert OpenOffice Calc ODS to PDF
@router.post("/ods-to-pdf", response_model=PDFConversionResponse)
async def convert_ods_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert OpenOffice Calc ODS to PDF."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "office")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="ods-to-pdf",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="ods",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine desired output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )
        
        # Convert ODS to PDF
        result_path = PDFConversionService.ods_to_pdf(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="ODS converted to PDF successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert PDF to Excel
@router.post("/pdf-to-excel", response_model=PDFConversionResponse)
async def convert_pdf_to_excel_extract(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to Excel (extract tabular data)."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "pdf")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="pdf-to-excel",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine desired output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".xlsx",
        )
        
        # Convert PDF to Excel
        result_path = PDFConversionService.pdf_to_excel_extract(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="xlsx"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PDF converted to Excel successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert PDF to Word
@router.post("/pdf-to-word", response_model=PDFConversionResponse)
async def convert_pdf_to_word_extract(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to Word document."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "pdf")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="pdf-to-word",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine desired output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".docx",
        )
        
        # Convert PDF to Word
        result_path = PDFConversionService.pdf_to_word_extract(input_path, output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="docx"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PDF converted to Word successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


@router.post("/pdf-to-jpg", response_model=PDFConversionResponse)
async def convert_pdf_to_jpg(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Convert PDF pages to JPG images.
    """
    input_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "pdf")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="pdf-to-jpg",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Derive a safe base name from either custom name or original filename
        base_name, _ = os.path.splitext(input_filename or "pdf_images")
        desired_base = (filename or base_name).strip()

        # Sanitize base name
        sanitized_base = re.sub(r"[^A-Za-z0-9._-]+", "_", desired_base).strip("._")
        if not sanitized_base:
            sanitized_base = "pdf_images"

        # Create a dedicated output folder
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
        
        # Convert
        result_files = PDFConversionService.pdf_to_image(input_path, folder_path, "jpg")

        # Rename files
        renamed_files = []
        for idx, src_path in enumerate(result_files, start=1):
            new_name = f"{folder_name}_page_{idx}.jpg"
            new_path = os.path.join(folder_path, new_name)
            try:
                os.replace(src_path, new_path)
            except Exception:
                new_path = src_path
            renamed_files.append(new_path)

        # Zip the folder into a single downloadable archive
        import shutil
        zip_base = os.path.join(output_root, folder_name)
        zip_path = shutil.make_archive(zip_base, 'zip', folder_path)
        zip_filename = os.path.basename(zip_path)  # e.g. MCPArchitecture.zip
        # Clean up the image folder (keep only the zip)
        shutil.rmtree(folder_path, ignore_errors=True)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=zip_filename,
            output_file_type="zip"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message=f"PDF converted to {len(renamed_files)} JPG images",
            output_filename=zip_filename,
            download_url=f"/api/v1/pdfconversiontools/download/{zip_filename}",
            pages_processed=len(renamed_files),
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None)


@router.post("/pdf-to-png", response_model=PDFConversionResponse)
async def convert_pdf_to_png(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF pages to PNG images."""
    input_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "pdf")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="pdf-to-png",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Derive a safe base name
        base_name, _ = os.path.splitext(input_filename or "pdf_images")
        desired_base = (filename or base_name).strip()

        # Sanitize base name
        sanitized_base = re.sub(r"[^A-Za-z0-9._-]+", "_", desired_base).strip("._")
        if not sanitized_base:
            sanitized_base = "pdf_images"

        # Create output folder
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
        
        # Convert
        result_files = PDFConversionService.pdf_to_image(input_path, folder_path, "png")

        # Rename files
        renamed_files = []
        for idx, src_path in enumerate(result_files, start=1):
            new_name = f"{folder_name}_page_{idx}.png"
            new_path = os.path.join(folder_path, new_name)
            try:
                os.replace(src_path, new_path)
            except Exception:
                new_path = src_path
            renamed_files.append(new_path)

        # Zip the folder into a single downloadable archive
        import shutil
        zip_base = os.path.join(output_root, folder_name)
        zip_path = shutil.make_archive(zip_base, 'zip', folder_path)
        zip_filename = os.path.basename(zip_path)  # e.g. MCPArchitecture.zip
        # Clean up the image folder (keep only the zip)
        shutil.rmtree(folder_path, ignore_errors=True)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=zip_filename,
            output_file_type="zip"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message=f"PDF converted to {len(renamed_files)} PNG images",
            output_filename=zip_filename,
            download_url=f"/api/v1/pdfconversiontools/download/{zip_filename}",
            pages_processed=len(renamed_files),
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None)


@router.post("/pdf-to-tiff", response_model=PDFConversionResponse)
async def convert_pdf_to_tiff(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF pages to TIFF images."""
    input_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "pdf")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="pdf-to-tiff",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Derive a safe base name
        base_name, _ = os.path.splitext(input_filename or "pdf_images")
        desired_base = (filename or base_name).strip()

        sanitized_base = re.sub(r"[^A-Za-z0-9._-]+", "_", desired_base).strip("._")
        if not sanitized_base:
            sanitized_base = "pdf_images"

        # Create output folder
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

        # Convert
        result_files = PDFConversionService.pdf_to_image(input_path, folder_path, "tiff")

        # Rename files
        renamed_files = []
        for idx, src_path in enumerate(result_files, start=1):
            new_name = f"{folder_name}_page_{idx}.tiff"
            new_path = os.path.join(folder_path, new_name)
            try:
                os.replace(src_path, new_path)
            except Exception:
                new_path = src_path
            renamed_files.append(new_path)

        # Zip the folder into a single downloadable archive
        import shutil
        zip_base = os.path.join(output_root, folder_name)
        zip_path = shutil.make_archive(zip_base, 'zip', folder_path)
        zip_filename = os.path.basename(zip_path)
        shutil.rmtree(folder_path, ignore_errors=True)

        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=zip_filename,
            output_file_type="zip"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message=f"PDF converted to {len(renamed_files)} TIFF images",
            output_filename=zip_filename,
            download_url=f"/api/v1/pdfconversiontools/download/{zip_filename}",
            pages_processed=len(renamed_files),
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None)


# Convert PDF to SVG
@router.post("/pdf-to-svg", response_model=PDFConversionResponse)
async def convert_pdf_to_svg(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF pages to SVG files."""
    input_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "pdf")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="pdf-to-svg",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Base name handling
        base_name, _ = os.path.splitext(input_filename or "pdf_images")
        desired_base = (filename or base_name).strip()

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

        # Convert
        result_files = PDFConversionService.pdf_to_svg(input_path, folder_path)

        renamed_files = []
        for idx, src_path in enumerate(result_files, start=1):
            new_name = f"{folder_name}_page_{idx}.svg"
            new_path = os.path.join(folder_path, new_name)
            try:
                os.replace(src_path, new_path)
            except Exception:
                new_path = src_path
            renamed_files.append(new_path)

        # Zip the folder into a single downloadable archive
        import shutil
        zip_base = os.path.join(output_root, folder_name)
        zip_path = shutil.make_archive(zip_base, 'zip', folder_path)
        zip_filename = os.path.basename(zip_path)
        shutil.rmtree(folder_path, ignore_errors=True)

        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=zip_filename,
            output_file_type="zip"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message=f"PDF converted to {len(renamed_files)} SVG files",
            output_filename=zip_filename,
            download_url=f"/api/v1/pdfconversiontools/download/{zip_filename}",
            pages_processed=len(renamed_files),
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None)


# Convert PDF to HTML
@router.post("/pdf-to-html", response_model=PDFConversionResponse)
async def convert_pdf_to_html(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to HTML."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "pdf")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="pdf-to-html",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id
        
        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".html",
        )
        
        # Convert
        result_path = PDFConversionService.pdf_to_html(input_path, output_path)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="html"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PDF converted to HTML successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Convert PDF to Text
@router.post("/pdf-to-text", response_model=PDFConversionResponse)
async def convert_pdf_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to plain text."""
    input_path = None
    output_path = None
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
            conversion_type="pdf-to-text",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        # Determine desired output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".txt",
        )

        # Convert
        result_path = PDFConversionService.pdf_to_text(input_path, output_path)

        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="txt"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PDF converted to text successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )

    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Get supported formats
@router.get("/supported-formats")
async def get_supported_formats():
    """Get supported input and output formats."""
    try:
        formats = PDFConversionService.get_supported_formats()
        return {
            "success": True,
            "formats": formats,
            "message": "Supported formats retrieved successfully"
        }
    except Exception as e:
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )


# PDF Merge
@router.post("/merge", response_model=PDFConversionResponse)
async def merge_pdfs(
    request: Request,
    files: Optional[List[UploadFile]] = File(None),
    file_keys: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Merge multiple PDF files into one."""
    input_paths = []
    output_path = None
    success = False
    log_id = None
    original_names: List[str] = []
    total_size = 0
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Handle multiple inputs
        # 1. Direct uploads
        if files:
            for file in files:
                FileService.validate_file(file, "pdf")
                total_size += file.size if hasattr(file, 'size') else 0 # size attribute might not be available in all fastapi versions, but usually is
                if total_size == 0:
                   file.file.seek(0, 2)
                   total_size += file.file.tell()
                   file.file.seek(0)
                
                input_path = FileService.save_uploaded_file(file)
                input_paths.append(input_path)
                original_names.append(os.path.splitext(file.filename or "file")[0])

        # 2. S3 keys (comma separated)
        if file_keys:
            keys = [k.strip() for k in file_keys.split(",") if k.strip()]
            for key in keys:
                path, fname, size = FileService.get_file_input(None, key, "pdf")
                input_paths.append(path)
                total_size += size
                original_names.append(os.path.splitext(fname)[0])

        if len(input_paths) < 2:
            raise create_error_response(
                error_type="ValidationError",
                message="Please select at least 2 PDF files before merging.",
                status_code=400
            )

        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="pdf-merge",
            input_filename=f"{len(input_paths)} files",
            input_file_size=total_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (filename or "_".join(original_names[:3])).strip()
        if not desired_name: desired_name = "merged"
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )
        
        # Merge
        result_path = PDFConversionService.merge_pdfs(input_paths, output_path)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PDFs merged successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except HTTPException:
        raise
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        for path in input_paths:
            if path:
                PDFConversionService.cleanup_temp_files(path)
        if not success and output_path and os.path.exists(output_path):
            try: os.remove(output_path)
            except: pass


# PDF Split
@router.post("/split", response_model=PDFConversionResponse)
async def split_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    split_type: str = Form("every_page"),
    page_ranges: Optional[str] = Form(None),
    output_prefix: Optional[str] = Form(None),
    zip: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Split PDF into multiple files."""
    input_path = None
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
            conversion_type="pdf-split",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine split type and ranges
        ranges = None
        if page_ranges:
            ranges = [r.strip() for r in page_ranges.split(',')]

        st = (split_type or "").strip().lower()
        if st == "" and ranges:
            st = "page_ranges"
        elif st == "":
            st = "every_page"

        # Split
        result = PDFConversionService.split_pdf(
            input_path=input_path,
            split_type=st,
            ranges=ranges,
            output_prefix=output_prefix,
            zip_output=zip,
        )

        folder_name = result.get("folder_name")
        files_payload = [
            {
                "filename": item["filename"],
                "download_url": f"/download/{folder_name}/{item['filename']}" if folder_name else f"/download/{item['filename']}",
                "pages": item.get("pages", [])
            }
            for item in result.get("files", [])
        ]

        # Calculate output file size
        output_size = 0
        if result.get("zip_filename"):
            zip_path = os.path.join(settings.output_dir, result["zip_filename"])
            if os.path.exists(zip_path):
                output_size = os.path.getsize(zip_path)
        elif folder_name:
            folder_path = os.path.join(settings.output_dir, folder_name)
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                for item in result.get("files", []):
                    file_p = os.path.join(folder_path, item["filename"])
                    if os.path.exists(file_p):
                        output_size += os.path.getsize(file_p)

        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=result.get("zip_filename") or folder_name,
            output_file_size=output_size,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message=f"PDF split into {result.get('count', 0)} files",
            output_filename=result.get("zip_filename"),
            download_url=(f"/download/{result['zip_filename']}" if result.get("zip_filename") else None),
            extracted_data={"files": files_payload}
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        if input_path:
            PDFConversionService.cleanup_temp_files(input_path)


# PDF Compress
@router.post("/compress", response_model=PDFConversionResponse)
async def compress_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    compression_level: str = Form("medium"),
    target_reduction_pct: Optional[int] = Form(None),
    max_image_dpi: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """Compress PDF file."""
    input_path = None
    output_path = None
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
            conversion_type="pdf-compress",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine desired output filename
        desired_name = (filename or f"{os.path.splitext(input_filename)[0]}_compressed").strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )

        # Compress
        result_path = PDFConversionService.compress_pdf(
            input_path,
            output_path,
            compression_level,
            target_reduction_pct,
            max_image_dpi,
        )
        
        # Get sizes
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(result_path)
        
        achieved_reduction = None
        if original_size > 0:
            achieved_reduction = round(((original_size - compressed_size) * 100.0) / original_size, 2)

        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PDF compressed successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}",
            file_size_before=original_size,
            file_size_after=compressed_size,
            extracted_data={
                "compression": {
                    "level": compression_level,
                    "target_reduction_pct": target_reduction_pct,
                    "achieved_reduction_pct": achieved_reduction,
                }
            }
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except HTTPException:
        raise
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Remove Pages
@router.post("/remove-pages", response_model=PDFConversionResponse)
async def remove_pages(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    pages_to_remove: str = Form(...),
    db: Session = Depends(get_db)
):
    """Remove specific pages from PDF."""
    input_path = None
    output_path = None
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
            conversion_type="pdf-remove-pages",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Parse pages to remove
        tokens = [t.strip() for t in re.split(r'[\,\s]+', pages_to_remove) if t.strip()]
        pages_list: List[int] = []
        for token in tokens:
            if '-' in token:
                s, e = token.split('-', 1)
                start = int(s)
                end = int(e)
                if start > end: start, end = end, start
                pages_list.extend(list(range(start, end + 1)))
            else:
                pages_list.append(int(token))
        
        # Remove duplicates preserving order
        seen = set()
        pages = [x for x in pages_list if not (x in seen or seen.add(x))]
        
        # Validation
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        invalid_pages = [p for p in pages if p < 1 or p > total_pages]
        if invalid_pages:
            raise create_error_response(
                error_type="PDFRemovePagesError",
                message=f"Invalid page numbers: {sorted(invalid_pages)}. Valid page range is 1-{total_pages}",
                details={"invalid_pages": sorted(invalid_pages), "total_pages": total_pages},
                status_code=400,
            )

        # Determine desired output filename
        desired_name = (filename or f"{os.path.splitext(input_filename)[0]}_pages_removed").strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )

        # Remove pages
        result_path = PDFConversionService.remove_pages(input_path, output_path, pages)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message=f"Pages removed successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except HTTPException:
        raise
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Extract Pages
@router.post("/extract-pages", response_model=PDFConversionResponse)
async def extract_pages(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    pages_to_extract: str = Form(...),
    db: Session = Depends(get_db)
):
    """Extract specific pages from PDF."""
    input_path = None
    output_path = None
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
            conversion_type="pdf-extract-pages",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Parse pages to extract
        tokens = [t.strip() for t in re.split(r'[\,\s]+', pages_to_extract) if t.strip()]
        pages_list: List[int] = []
        for token in tokens:
            if '-' in token:
                s, e = token.split('-', 1)
                start = int(s)
                end = int(e)
                if start > end: start, end = end, start
                pages_list.extend(list(range(start, end + 1)))
            else:
                pages_list.append(int(token))
        
        # Remove duplicates preserving order
        seen = set()
        pages = [x for x in pages_list if not (x in seen or seen.add(x))]
        
        # Validation
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        invalid_pages = [p for p in pages if p < 1 or p > total_pages]
        if invalid_pages:
            raise create_error_response(
                error_type="PDFExtractPagesError",
                message=f"Invalid page numbers: {sorted(invalid_pages)}. Valid page range is 1-{total_pages}",
                details={"invalid_pages": sorted(invalid_pages), "total_pages": total_pages},
                status_code=400,
            )

        # Determine desired output filename
        desired_name = (filename or f"{os.path.splitext(input_filename)[0]}_extracted").strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )

        # Extract pages
        result_path = PDFConversionService.extract_pages(input_path, output_path, pages)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message=f"Pages extracted successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except HTTPException:
        raise
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Rotate PDF
@router.post("/rotate", response_model=PDFConversionResponse)
async def rotate_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    rotation: int = Form(90),
    db: Session = Depends(get_db)
):
    """Rotate PDF pages."""
    input_path = None
    output_path = None
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
            conversion_type="pdf-rotate",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine desired output filename
        desired_name = (filename or f"{os.path.splitext(input_filename)[0]}_rotated_{rotation}").strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )

        # Rotate
        result_path = PDFConversionService.rotate_pdf(input_path, output_path, rotation)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message=f"PDF rotated {rotation} degrees successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Add Watermark
@router.post("/add-watermark", response_model=PDFConversionResponse)
async def add_watermark(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    watermark_text: str = Form(...),
    position: str = Form("center"),
    db: Session = Depends(get_db)
):
    """Add watermark to PDF."""
    input_path = None
    output_path = None
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
            conversion_type="pdf-watermark",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine desired output filename
        desired_name = (filename or f"{os.path.splitext(input_filename)[0]}_watermarked").strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )

        # Add watermark
        result_path = PDFConversionService.add_watermark(input_path, output_path, watermark_text, position)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="Watermark added successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except HTTPException:
        raise
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Add Page Numbers
@router.post("/add-page-numbers", response_model=PDFConversionResponse)
async def add_page_numbers(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    position: str = Form("bottom-center"),
    start_page: int = Form(1),
    format: str = Form("{page}"),
    font_size: float = Form(12.0),
    db: Session = Depends(get_db)
):
    """Add page numbers to PDF."""
    input_path = None
    output_path = None
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
            conversion_type="pdf-page-numbers",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine desired output filename
        desired_name = (filename or f"{os.path.splitext(input_filename)[0]}_numbered").strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )

        # Add page numbers
        result_path = PDFConversionService.add_page_numbers(
            input_path,
            output_path,
            position,
            start_page,
            format,
            font_size,
        )
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="Page numbers added successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except HTTPException:
        raise
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Crop PDF
@router.post("/crop", response_model=PDFConversionResponse)
async def crop_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    x: int = Form(0),
    y: int = Form(0),
    width: int = Form(100),
    height: int = Form(100),
    db: Session = Depends(get_db)
):
    """Crop PDF pages."""
    input_path = None
    output_path = None
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
            conversion_type="pdf-crop",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine desired output filename
        desired_name = (filename or f"{os.path.splitext(input_filename)[0]}_cropped").strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )

        # Crop
        crop_box = {"x": x, "y": y, "width": width, "height": height}
        result_path = PDFConversionService.crop_pdf(input_path, output_path, crop_box)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PDF cropped successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except HTTPException:
        raise
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Protect PDF
@router.post("/protect", response_model=PDFConversionResponse)
async def protect_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Protect PDF with password."""
    input_path = None
    output_path = None
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
            conversion_type="pdf-protect",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine desired output filename
        desired_name = (filename or f"{os.path.splitext(input_filename)[0]}_protected").strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )

        # Protect
        result_path = PDFConversionService.protect_pdf(input_path, output_path, password)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PDF protected successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except HTTPException:
        raise
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Unlock PDF
@router.post("/unlock", response_model=PDFConversionResponse)
async def unlock_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Remove password protection from PDF."""
    input_path = None
    output_path = None
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
            conversion_type="pdf-unlock",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine desired output filename
        desired_name = (filename or f"{os.path.splitext(input_filename)[0]}_unlocked").strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )

        # Unlock
        result_path = PDFConversionService.unlock_pdf(input_path, output_path, password)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PDF unlocked successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except HTTPException:
        raise
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Repair PDF
@router.post("/repair", response_model=PDFConversionResponse)
async def repair_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Repair corrupted PDF."""
    input_path = None
    output_path = None
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
            conversion_type="pdf-repair",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine desired output filename
        desired_name = (filename or f"{os.path.splitext(input_filename)[0]}_repaired").strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".pdf",
        )

        # Repair
        result_path = PDFConversionService.repair_pdf(input_path, output_path)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="pdf"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message="PDF repaired successfully",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except HTTPException:
        raise
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Compare PDFs
@router.post("/compare", response_model=PDFConversionResponse)
async def compare_pdfs(
    request: Request,
    file1: Optional[UploadFile] = File(None),
    file1_key: Optional[str] = Form(None),
    file2: Optional[UploadFile] = File(None),
    file2_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Compare two PDFs."""
    input_path1 = None
    input_path2 = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling for file1
        input_path1, input_filename1, input_size1 = FileService.get_file_input(file1, file1_key, "pdf")
        # Standardized input handling for file2
        input_path2, input_filename2, input_size2 = FileService.get_file_input(file2, file2_key, "pdf")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="pdf-compare",
            input_filename=f"{input_filename1} vs {input_filename2}",
            input_file_size=input_size1 + input_size2,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine desired output filename
        base1 = os.path.splitext(input_filename1)[0]
        base2 = os.path.splitext(input_filename2)[0]
        desired_name = (filename or f"{base1}_vs_{base2}_comparison").strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".txt",
        )

        # Compare
        comparison_result = PDFConversionService.compare_pdfs(input_path1, input_path2, output_path)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="txt"
        )
        
        success = True
        return PDFConversionResponse(
            success=True,
            message=f"PDFs compared successfully. Found {comparison_result.get('differences_count', 0)} differences",
            output_filename=final_filename,
            download_url=f"/download/{final_filename}",
            extracted_data=comparison_result
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except HTTPException:
        raise
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        if input_path1: PDFConversionService.cleanup_temp_files(input_path1)
        if input_path2: PDFConversionService.cleanup_temp_files(input_path2)
        if not success and output_path and os.path.exists(output_path):
            try: os.remove(output_path)
            except: pass


# Get PDF Metadata
@router.post("/metadata")
async def get_pdf_metadata(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Get PDF metadata."""
    input_path = None
    output_path = None
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
            conversion_type="pdf-metadata",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Get metadata
        metadata = PDFConversionService.get_pdf_metadata(input_path)
        
        # Determine desired output filename
        desired_name = (filename or f"{os.path.splitext(input_filename)[0]}_metadata").strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".json",
        )
        
        # Save as JSON file for download
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                import json as _json
                _json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="json"
        )
        
        success = True
        return {
            "success": True,
            "message": "PDF metadata extracted successfully",
            "metadata": metadata,
            "output_filename": final_filename,
            "download_url": f"/download/{final_filename}",
        }
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Download converted file
@router.get("/download/{filename}")
async def download_file(filename: str, background_tasks: BackgroundTasks):
    """Download a converted file and clean up."""
    file_path = os.path.join(settings.output_dir, filename)
    return FileService.create_cleanup_response(file_path, filename, background_tasks)

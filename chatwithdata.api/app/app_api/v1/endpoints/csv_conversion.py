import json
import os
import logging
from typing import Optional, List, Any, Dict
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends, Request, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.app_services.csv_conversion_service import CSVConversionService
from app.app_services.conversion_log_service import ConversionLogService
from app.app_core.database import get_db
from app.app_api.v1.dependencies import get_user_id
from app.app_services.file_service import FileService
from app.app_core.config import settings
from app.app_services.s3_service import s3_service
from app.app_core.exceptions import (
    create_error_response,
    FileProcessingError,
    UnsupportedFileTypeError,
    FileSizeExceededError,
)
from app.app_models.schemas import ConversionResponse

logger = logging.getLogger(__name__)

router = APIRouter()


# HTML Table to CSV
@router.post("/html-table-to-csv", response_model=ConversionResponse)
async def convert_html_table_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert HTML table to CSV. Requires HTML file upload."""
    input_path = None
    output_path = None
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
            conversion_type="html-table-to-csv",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="html",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".csv",
        )
        
        # Read content
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        # Convert
        result = CSVConversionService.html_table_to_csv(content)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="csv"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="HTML table converted to CSV successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/csvconversiontools/download/{final_filename}",
            converted_data=result
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Excel to CSV
@router.post("/excel-to-csv", response_model=ConversionResponse)
async def convert_excel_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Excel file to CSV."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "office")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="excel-to-csv",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="xlsx", 
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".csv",
        )
        
        # Read content
        with open(input_path, "rb") as f:
            file_content = f.read()
            
        # Convert
        result = CSVConversionService.excel_to_csv(file_content)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="csv"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="Excel file converted to CSV successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/csvconversiontools/download/{final_filename}",
            converted_data=result
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# OpenOffice Calc ODS to CSV
@router.post("/ods-to-csv", response_model=ConversionResponse)
async def convert_ods_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert OpenOffice Calc ODS file to CSV."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "office")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="ods-to-csv",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="ods",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".csv",
        )
        
        # Read content
        with open(input_path, "rb") as f:
            file_content = f.read()
            
        # Convert
        result = CSVConversionService.ods_to_csv(file_content)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="csv"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="ODS file converted to CSV successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/csvconversiontools/download/{final_filename}",
            converted_data=result
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# CSV to Excel
@router.post("/csv-to-excel", response_model=ConversionResponse)
async def convert_csv_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert CSV to Excel file. Requires CSV file upload."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "csv")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="csv-to-excel",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="csv",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".xlsx",
        )
        
        # Read content
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        # Convert
        service_output_path = CSVConversionService.csv_to_excel(content)
        
        # Rename/Move to final output path
        if os.path.exists(service_output_path):
            import shutil
            shutil.move(service_output_path, output_path)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="xlsx"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="CSV converted to Excel successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/csvconversiontools/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# CSV to XML
@router.post("/csv-to-xml", response_model=ConversionResponse)
async def convert_csv_to_xml(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    root_name: str = Form("data"),
    db: Session = Depends(get_db)
):
    """Convert CSV to XML. Requires CSV file upload."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "csv")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="csv-to-xml",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="csv",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".xml",
        )
        
        # Read content
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        # Convert
        result = CSVConversionService.csv_to_xml(content, root_name)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="xml"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="CSV converted to XML successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/csvconversiontools/download/{final_filename}",
            converted_data=result
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# XML to CSV
@router.post("/xml-to-csv", response_model=ConversionResponse)
async def convert_xml_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert XML to CSV. Requires XML file upload."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "xml")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="xml-to-csv",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="xml",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".csv",
        )
        
        # Read content
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        # Convert
        result = CSVConversionService.xml_to_csv(content)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="csv"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="XML converted to CSV successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/csvconversiontools/download/{final_filename}",
            converted_data=result
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# PDF to CSV
@router.post("/pdf-to-csv", response_model=ConversionResponse)
async def convert_pdf_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to CSV. Requires PDF file upload."""
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
            conversion_type="pdf-to-csv",
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
            default_extension=".csv",
        )
        
        # Read content
        with open(input_path, "rb") as f:
            file_content = f.read()
            
        # Convert
        result = CSVConversionService.pdf_to_csv(file_content)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="csv"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="PDF converted to CSV successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/csvconversiontools/download/{final_filename}",
            converted_data=result
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# JSON to CSV
@router.post("/json-to-csv", response_model=ConversionResponse)
async def convert_json_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert JSON to CSV. Requires JSON file upload."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "json")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="json-to-csv",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="json",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".csv",
        )
        
        # Read content
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        # Parse JSON
        try:
            json_data = json.loads(content)
        except json.JSONDecodeError:
            raise FileProcessingError("Invalid JSON file")

        # Convert
        result = CSVConversionService.json_to_csv(json_data)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="csv"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="JSON converted to CSV successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/csvconversiontools/download/{final_filename}",
            converted_data=result
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# CSV to JSON
@router.post("/csv-to-json", response_model=ConversionResponse)
async def convert_csv_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert CSV to JSON. Requires CSV file upload."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "csv")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="csv-to-json",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="csv",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".json",
        )
        
        # Read content
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        # Convert
        result = CSVConversionService.csv_to_json(content)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="json"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="CSV converted to JSON successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/csvconversiontools/download/{final_filename}",
            converted_data=result
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# JSON Objects to CSV
@router.post("/json-objects-to-csv", response_model=ConversionResponse)
async def convert_json_objects_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert JSON objects to CSV. Requires JSON file upload."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "json")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="json-objects-to-csv",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="json",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".csv",
        )
        
        # Read content
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        # Parse JSON
        try:
             json_objects = json.loads(content)
             if not isinstance(json_objects, list):
                 raise FileProcessingError("JSON file must contain a list of objects")
        except json.JSONDecodeError:
            raise FileProcessingError("Invalid JSON file")

        # Convert
        result = CSVConversionService.json_objects_to_csv(json_objects)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="csv"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="JSON objects converted to CSV successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/csvconversiontools/download/{final_filename}",
            converted_data=result
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# BSON to CSV
@router.post("/bson-to-csv", response_model=ConversionResponse)
async def convert_bson_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert BSON file to CSV. Requires BSON file upload."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "bson")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="bson-to-csv",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="bson",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".csv",
        )
        
        # Read content
        with open(input_path, "rb") as f:
            file_content = f.read()
            
        # Convert
        result = CSVConversionService.bson_to_csv(file_content)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="csv"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="BSON file converted to CSV successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/csvconversiontools/download/{final_filename}",
            converted_data=result
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# SRT to CSV
@router.post("/srt-to-csv", response_model=ConversionResponse)
async def convert_srt_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT subtitle file to CSV. Requires SRT file upload."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "srt")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="srt-to-csv",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="srt",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".csv",
        )
        
        # Read content
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        # Convert
        result = CSVConversionService.srt_to_csv(content)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="csv"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="SRT file converted to CSV successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/csvconversiontools/download/{final_filename}",
            converted_data=result
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# CSV to SRT
@router.post("/csv-to-srt", response_model=ConversionResponse)
async def convert_csv_to_srt(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert CSV to SRT subtitle file. Requires CSV file upload."""
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "csv")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="csv-to-srt",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="csv",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        desired_name = (filename or input_filename).strip()
        output_path, final_filename = FileService.generate_output_path_with_filename(
            desired_name,
            default_extension=".srt",
        )
        
        # Read content
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        # Convert
        result = CSVConversionService.csv_to_srt(content)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type="srt"
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="CSV converted to SRT successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/csvconversiontools/download/{final_filename}",
            converted_data=result
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Download endpoint for generated files
@router.get("/download/{filename}")
async def download_file(filename: str, background_tasks: BackgroundTasks):
    """Download a generated file and clean up."""
    file_path = os.path.join(settings.output_dir, filename)
    return FileService.create_cleanup_response(file_path, filename, background_tasks)

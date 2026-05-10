import json
import os
import logging
from typing import Optional, Dict, Any, List, Union, Tuple
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends, Request, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.app_services.xml_conversion_service import XMLConversionService
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


# CSV to XML
@router.post("/csv-to-xml", response_model=ConversionResponse)
async def convert_csv_to_xml(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    root_name: str = Form("data"),
    record_name: str = Form("record"),
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
            
        if not content.strip():
             raise FileProcessingError("CSV file is empty")

        # Convert
        result = XMLConversionService.csv_to_xml(content, root_name, record_name)
        
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
            download_url=f"/api/v1/xmlconversiontools/download/{final_filename}",
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


# Excel to XML
@router.post("/excel-to-xml", response_model=ConversionResponse)
async def convert_excel_to_xml(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    root_name: str = Form("data"),
    record_name: str = Form("record"),
    db: Session = Depends(get_db)
):
    """Convert Excel file to XML."""
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
            conversion_type="excel-to-xml",
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
            default_extension=".xml",
        )
        
        # Read content
        with open(input_path, "rb") as f:
            file_content = f.read()
            
        # Convert
        result = XMLConversionService.excel_to_xml(file_content, root_name, record_name)
        
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
            message="Excel file converted to XML successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/xmlconversiontools/download/{final_filename}",
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


# XML to JSON
@router.post("/xml-to-json", response_model=ConversionResponse)
async def convert_xml_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert XML to JSON. Requires XML file upload."""
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
            conversion_type="xml-to-json",
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
            default_extension=".json",
        )
        
        # Read content
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        if not content.strip():
            raise FileProcessingError("XML file is empty")
        
        # Convert XML to JSON
        json_result = XMLConversionService.xml_to_json(content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_result)
        
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
            message="XML converted to JSON successfully",
            converted_data=json_result,
            output_filename=final_filename,
            download_url=f"/api/v1/xmlconversiontools/download/{final_filename}"
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

        if not content.strip():
            raise FileProcessingError("XML file is empty")

        # Convert
        result = XMLConversionService.xml_to_csv(content)
        
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
            converted_data=result,
            output_filename=final_filename,
            download_url=f"/api/v1/xmlconversiontools/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# XML to Excel
@router.post("/xml-to-excel", response_model=ConversionResponse)
async def convert_xml_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert XML to Excel file. Requires XML file upload."""
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
            conversion_type="xml-to-excel",
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
            default_extension=".xlsx",
        )
        
        # Read content
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        if not content.strip():
            raise FileProcessingError("XML file is empty")

        # Convert
        service_output_path = XMLConversionService.xml_to_excel(content)
        
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
            message="XML converted to Excel successfully",
            output_filename=final_filename,
            download_url=f"/api/v1/xmlconversiontools/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# Fix XML Escaping
@router.post("/fix-xml-escaping", response_model=ConversionResponse)
async def fix_xml_escaping(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Fix XML escaping issues. Requires XML file upload."""
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
            conversion_type="fix-xml-escaping",
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
            default_extension=".xml",
        )
        
        # Read content
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        if not content.strip():
            raise FileProcessingError("XML file is empty")

        # Convert
        result = XMLConversionService.fix_xml_escaping(content)
        
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
            message="XML escaping fixed successfully",
            converted_data=result,
            output_filename=final_filename,
            download_url=f"/api/v1/xmlconversiontools/download/{final_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else (output_path if 'output_path' in locals() else None))


# XML/XSD Validator
@router.post("/xml-xsd-validator", response_model=ConversionResponse)
async def validate_xml_xsd(
    request: Request,
    file_xml: Optional[UploadFile] = File(None),
    file_xml_key: Optional[str] = Form(None),
    file_xsd: Optional[UploadFile] = File(None),
    file_xsd_key: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Validate XML against XSD schema. Requires XML file. XSD file is optional."""
    input_path = None
    xsd_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Standardized input handling for XML
        input_path, input_filename, input_size = FileService.get_file_input(file_xml, file_xml_key, "xml")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="xml-xsd-validator",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="xml",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Get XML Content
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            xml_text = f.read()
        
        if not xml_text.strip():
            raise FileProcessingError("XML file is empty")

        # Get XSD Content (Optional)
        xsd_text = None
        if file_xsd or file_xsd_key:
             xsd_path, _, _ = FileService.get_file_input(file_xsd, file_xsd_key, "xsd")
             with open(xsd_path, "r", encoding="utf-8", errors="replace") as f:
                 xsd_text = f.read()
        
        result = XMLConversionService.xml_xsd_validator(xml_text, xsd_text)
        
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=None, # No output file for validation
            output_file_type=None
        )
        
        success = True
        return ConversionResponse(
            success=True,
            message="XML validation completed successfully",
            converted_data=json.dumps(result)
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None)
        if xsd_path: FileService.cleanup_files(xsd_path, None)


# JSON to XML
@router.post("/json-to-xml", response_model=ConversionResponse)
async def convert_json_to_xml(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    root_name: str = Form("root"),
    db: Session = Depends(get_db)
):
    """Convert JSON to XML. Requires JSON file upload."""
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
            conversion_type="json-to-xml",
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
            default_extension=".xml",
        )
        
        # Read content
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        if not content.strip():
            raise FileProcessingError("JSON file is empty")

        # Parse JSON
        try:
            json_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise FileProcessingError(f"Invalid JSON format: {str(e)}")

        # Convert
        result = XMLConversionService.json_to_xml(json_data, root_name)
        
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
            message="JSON converted to XML successfully",
            converted_data=result,
            output_filename=final_filename,
            download_url=f"/api/v1/xmlconversiontools/download/{final_filename}"
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

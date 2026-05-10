import json
import os
import uuid
import logging
from datetime import date, datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.app_core.database import get_db
from app.app_services.conversion_log_service import ConversionLogService
from app.app_api.v1.dependencies import get_user_id

from app.app_models.schemas import ConversionResponse
from app.app_services.s3_service import s3_service
from app.app_services.json_conversion_service import JSONConversionService
from app.app_services.pdf_conversion_service import PDFConversionService
from app.app_services.image_conversion_service import ImageConversionService
from app.app_services.file_service import FileService
from app.app_core.config import settings
from app.app_core.exceptions import (
    FileProcessingError,
    UnsupportedFileTypeError,
    FileSizeExceededError,
    create_error_response,
)



# Custom JSON Encoder to handle date/datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


# Custom dependency to handle optional file upload (handles empty string from Swagger UI)
async def optional_file_upload(file: Union[UploadFile, str, None] = File(default=None)) -> Optional[UploadFile]:
    """Handle file upload that may be None, empty string, or actual file."""
    if file is None or file == "" or (isinstance(file, str) and not file.strip()):
        return None
    if isinstance(file, UploadFile):
        return file
    return None


logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class XMLToJSONRequest(BaseModel):
    xml_content: str


class JSONToXMLRequest(BaseModel):
    json_data: Dict[str, Any]
    root_name: Optional[str] = "root"


class JSONFormatRequest(BaseModel):
    json_data: Dict[str, Any]


class JSONValidateRequest(BaseModel):
    json_content: str


class JSONToCSVRequest(BaseModel):
    json_data: List[Dict[str, Any]]
    delimiter: Optional[str] = ","


class JSONToYAMLRequest(BaseModel):
    json_data: Dict[str, Any]


class YAMLToJSONRequest(BaseModel):
    yaml_content: str


class JSONObjectsToCSVRequest(BaseModel):
    json_objects: List[Dict[str, Any]]
    delimiter: Optional[str] = ","


class JSONObjectsToExcelRequest(BaseModel):
    json_objects: List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _build_download_url(filename: str) -> str:
    """Build consistent download url for generated files."""
    return f"/api/v1/jsonconversiontools/download/{filename}"


def _cleanup_files(*paths: Optional[str]) -> None:
    """Cleanup temporary files if they exist."""
    for path in paths:
        if path:
            FileService.cleanup_file(path)


# ---------------------------------------------------------------------------
# 1. AI: Convert PDF to JSON
# ---------------------------------------------------------------------------

@router.post("/ai/pdf-to-json", response_model=ConversionResponse)
async def ai_convert_pdf_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """AI-assisted PDF to JSON conversion with structured extraction."""
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
            conversion_type="ai-pdf-to-json",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="pdf",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        if filename and filename.strip() and filename.lower() != "string":
            if not filename.lower().endswith('.json'):
                filename += '.json'
            output_filename = filename
        else:
            base_name = os.path.splitext(input_filename)[0] if input_filename else "pdf_to_json"
            output_filename = f"{base_name}.json"
        
        output_path = os.path.join(settings.output_dir, output_filename)
        os.makedirs(settings.output_dir, exist_ok=True)

        result_path = PDFConversionService.pdf_to_json(input_path, output_path)
        result_filename = os.path.basename(result_path)
        
        # Upload to S3 if configured
        if settings.s3_bucket:
            try:
                s3_key = s3_service.upload_file_to_s3(result_path, result_filename, "outputs")
                if s3_key:
                    logger.info(f"File uploaded to S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to upload output to S3: {e}")

        # Update log on success
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success",
                output_filename=result_filename,
                output_file_type="json"
            )

        success = True
        return ConversionResponse(
            success=True,
            message="AI: PDF converted to JSON successfully",
            output_filename=result_filename,
            download_url=_build_download_url(result_filename),
        )

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in ai_convert_pdf_to_json: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during conversion",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path, None if success else output_path)



# ---------------------------------------------------------------------------
# 2. AI: Convert PNG to JSON
# ---------------------------------------------------------------------------

@router.post("/ai/png-to-json", response_model=ConversionResponse)
async def ai_convert_png_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """AI-assisted image to JSON conversion with OCR text extraction."""
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
            conversion_type="ai-png-to-json",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="png",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        if filename and filename.strip() and filename.lower() != "string":
            if not filename.lower().endswith('.json'):
                filename += '.json'
            output_filename = filename
        else:
            base_name = os.path.splitext(input_filename)[0] if input_filename else "png_to_json"
            output_filename = f"{base_name}.json"
        
        output_path = os.path.join(settings.output_dir, output_filename)
        os.makedirs(settings.output_dir, exist_ok=True)
        
        # Convert image to JSON
        result_path = ImageConversionService.image_to_json(input_path, output_path=output_path)
        result_filename = os.path.basename(result_path)
        
        # Upload to S3 if configured
        if settings.s3_bucket:
            try:
                s3_key = s3_service.upload_file_to_s3(result_path, result_filename, "outputs")
                if s3_key:
                    logger.info(f"File uploaded to S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to upload output to S3: {e}")

        # Update log on success
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success",
                output_filename=result_filename,
                output_file_type="json"
            )

        success = True
        return ConversionResponse(
            success=True,
            message="AI: PNG converted to JSON successfully",
            output_filename=result_filename,
            download_url=_build_download_url(result_filename),
        )

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in ai_convert_png_to_json: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during conversion",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path, None if success else output_path)





# ---------------------------------------------------------------------------
# 3. AI: Convert JPG to JSON
# ---------------------------------------------------------------------------

@router.post("/ai/jpg-to-json", response_model=ConversionResponse)
async def ai_convert_jpg_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """AI-assisted JPG to JSON conversion with OCR text extraction."""
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
            conversion_type="ai-jpg-to-json",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="jpg",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        if filename and filename.strip() and filename.lower() != "string":
            if not filename.lower().endswith('.json'):
                filename += '.json'
            output_filename = filename
        else:
            base_name = os.path.splitext(input_filename)[0] if input_filename else "jpg_to_json"
            output_filename = f"{base_name}.json"
        
        output_path = os.path.join(settings.output_dir, output_filename)
        os.makedirs(settings.output_dir, exist_ok=True)
        
        # Convert image to JSON
        result_path = ImageConversionService.image_to_json(input_path, output_path=output_path)
        result_filename = os.path.basename(result_path)
        
        # Upload to S3 if configured
        if settings.s3_bucket:
            try:
                s3_key = s3_service.upload_file_to_s3(result_path, result_filename, "outputs")
                if s3_key:
                    logger.info(f"File uploaded to S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to upload output to S3: {e}")

        # Update log on success
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success",
                output_filename=result_filename,
                output_file_type="json"
            )

        success = True
        return ConversionResponse(
            success=True,
            message="AI: JPG converted to JSON successfully",
            output_filename=result_filename,
            download_url=_build_download_url(result_filename),
        )

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in ai_convert_jpg_to_json: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during conversion",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path, None if success else output_path)



# ---------------------------------------------------------------------------
# 4. Convert XML to JSON
# ---------------------------------------------------------------------------

@router.post("/xml-to-json", response_model=ConversionResponse)
async def convert_xml_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Convert XML to JSON format.
    Supports both direct upload and S3 file key.
    """
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)
        
        # Standardized input handling (Direct Upload or S3)
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
        
        # Read XML content
        with open(input_path, "r", encoding="utf-8") as f:
            xml_data = f.read()

        json_result = JSONConversionService.xml_to_json(xml_data)
        json_string = json.dumps(json_result, indent=2, cls=DateTimeEncoder)

        # Determine output filename
        if filename and filename.strip() and filename.lower() != "string":
            if not filename.lower().endswith('.json'):
                filename += '.json'
            output_filename = filename
        else:
            base_name = os.path.splitext(input_filename)[0] if input_filename else "xml_to_json"
            output_filename = f"{base_name}.json"

        output_path = os.path.join(settings.output_dir, output_filename)
        os.makedirs(settings.output_dir, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_string)

        result_filename = os.path.basename(output_path)
        
        # Upload to S3 if configured
        if settings.s3_bucket:
            try:
                s3_key = s3_service.upload_file_to_s3(output_path, result_filename, "outputs")
                if s3_key:
                    logger.info(f"File uploaded to S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to upload output to S3: {e}")

        # Update log on success
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success",
                output_filename=result_filename,
                output_file_type="json"
            )

        success = True
        return ConversionResponse(
            success=True,
            message="XML converted to JSON successfully",
            output_filename=result_filename,
            download_url=_build_download_url(result_filename),
        )

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError, ValueError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in convert_xml_to_json: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during conversion",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path, None if success else output_path)


# ---------------------------------------------------------------------------
# 5. JSON Formatter
# ---------------------------------------------------------------------------


@router.post("/json-formatter", response_model=ConversionResponse)
async def format_json(
    request: Request,
    json_text: Optional[str] = Form(default=None),
    filename: Optional[str] = Form(default=None),
    file_key: Optional[str] = Form(default=None),
    indent: int = Form(default=2),
    file: Union[UploadFile, str, None] = File(default=None),
    db: Session = Depends(get_db)
):
    """Format JSON with proper indentation. Supports file upload, S3 key, and direct JSON text."""
    input_path = None
    output_path = None
    json_data_str = None
    success = False
    log_id = None
    
    # Check if a file source is provided (UploadFile or S3 key)
    has_file_source = (
        (file is not None and hasattr(file, 'filename') and file.filename) or 
        (file_key and file_key.lower().strip() not in ["string", "null", "none", ""])
    )
    
    # Get user_id
    user_id = await get_user_id(request, db)

    try:
        # 1. Handle File Input (Priority 1)
        if has_file_source:
            input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "json")
            with open(input_path, "r", encoding="utf-8") as f:
                json_data_str = f.read()
            input_identifier = input_filename
        # 2. Handle Text Input (Priority 2)
        elif json_text and json_text.strip().lower() not in ['string', 'null', 'none', '']:
            json_data_str = json_text.strip()
            input_identifier = "json-text"
            input_size = len(json_data_str)
        else:
            raise FileProcessingError("Please provide either a JSON file, a storage key, or JSON text")

        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="json-formatter",
            input_filename=input_identifier,
            input_file_size=input_size,
            input_file_type="json",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Parse and Format JSON
        try:
            parsed_json = json.loads(json_data_str)
        except json.JSONDecodeError as e:
            raise FileProcessingError(f"Invalid JSON format: {str(e)}")
        
        formatted_json = json.dumps(parsed_json, indent=indent, ensure_ascii=False, cls=DateTimeEncoder)
        
        # Determine output filename if we need to save to file
        # 3. Create output file (always enabled for download)
        if filename and filename.strip() and filename.lower() != "string":
            if not filename.lower().endswith('.json'):
                filename += '.json'
            output_filename = filename
        else:
            if has_file_source and input_identifier:
                base_name = os.path.splitext(input_identifier)[0]
                output_filename = f"{base_name}_formatted.json"
            else:
                output_filename = "formatted_json.json"
            
        output_path = os.path.join(settings.output_dir, output_filename)
        os.makedirs(settings.output_dir, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(formatted_json)
        
        result_filename = os.path.basename(output_path)

        # Upload to S3 if configured
        if settings.s3_bucket:
            try:
                s3_service.upload_file_to_s3(output_path, result_filename, "outputs")
            except Exception as e:
                logger.error(f"Failed to upload output to S3: {e}")

        # Update log
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success",
                output_filename=result_filename,
                output_file_type="json"
            )

        success = True
        return ConversionResponse(
            success=True,
            message="JSON formatted successfully",
            output_filename=result_filename,
            download_url=_build_download_url(result_filename),
            converted_data=formatted_json,
        )

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError, ValueError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in format_json: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during formatting",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path, output_path if not success else None)


# ---------------------------------------------------------------------------
# 6. JSON Validator
# ---------------------------------------------------------------------------

@router.post("/json-validator")
async def validate_json(
    request: Request,
    json_text: Optional[str] = Form(default=None),
    file_key: Optional[str] = Form(default=None),
    file: Union[UploadFile, str, None] = File(default=None),
    db: Session = Depends(get_db)
):
    """Validate JSON. Supports file upload, S3 key, and direct JSON text."""
    input_path = None
    json_data_str = None
    log_id = None
    
    # Check if a file source is provided
    has_file_source = (
        (file is not None and hasattr(file, 'filename') and file.filename) or 
        (file_key and file_key.lower().strip() not in ["string", "null", "none", ""])
    )
    
    # Get user_id
    user_id = await get_user_id(request, db)

    try:
        # 1. Handle File Input (Priority 1)
        if has_file_source:
            input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "json")
            with open(input_path, "r", encoding="utf-8") as f:
                json_data_str = f.read()
            input_identifier = input_filename
        # 2. Handle Text Input (Priority 2)
        elif json_text and json_text.strip().lower() not in ['string', 'null', 'none', '']:
            json_data_str = json_text.strip()
            input_identifier = "json-text"
            input_size = len(json_data_str)
        else:
            raise FileProcessingError("Please provide either a JSON file, a storage key, or JSON text")

        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="json-validator",
            input_filename=input_identifier,
            input_file_size=input_size,
            input_file_type="json",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Validate JSON
        is_valid = False
        error_message = None
        line_number = None
        column_number = None
        
        try:
            json.loads(json_data_str)
            is_valid = True
        except json.JSONDecodeError as e:
            is_valid = False
            error_message = str(e.msg)
            line_number = e.lineno
            column_number = e.colno
        except Exception as e:
            is_valid = False
            error_message = str(e)
        
        # Prepare response
        result = {
            "valid": is_valid,
            "message": "JSON is valid!" if is_valid else f"Invalid JSON: {error_message}",
        }
        
        if not is_valid:
            result["error"] = {
                "message": error_message,
                "line": line_number,
                "column": column_number,
            }
        
        # Log update
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success" if is_valid else "failed",
                error_message=None if is_valid else error_message,
                output_file_type="json"
            )
        
        return result

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in validate_json: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during validation",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path)


# ---------------------------------------------------------------------------
# 7. Convert JSON to XML
# ---------------------------------------------------------------------------

@router.post("/json-to-xml", response_model=ConversionResponse)
async def convert_json_to_xml(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    root_name: Optional[str] = Form("root"),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Convert JSON to XML format.
    Supports both direct upload and S3 file key.
    """
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)
        
        # Standardized input handling (Direct Upload or S3)
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
        if filename and filename.strip() and filename.lower() != "string":
            if not filename.lower().endswith('.xml'):
                filename += '.xml'
            output_filename = filename
        else:
            base_name = os.path.splitext(input_filename)[0] if input_filename else "json_to_xml"
            output_filename = f"{base_name}.xml"

        output_path = os.path.join(settings.output_dir, output_filename)
        os.makedirs(settings.output_dir, exist_ok=True)
        
        # Perform conversion
        with open(input_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            
        xml_result = JSONConversionService.json_to_xml(json_data, root_name=root_name)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(xml_result)

        result_filename = os.path.basename(output_path)
        
        # Upload to S3 if configured
        if settings.s3_bucket:
            try:
                s3_key = s3_service.upload_file_to_s3(output_path, result_filename, "outputs")
                if s3_key:
                    logger.info(f"File uploaded to S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to upload output to S3: {e}")

        # Update log on success
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success",
                output_filename=result_filename,
                output_file_type="xml"
            )

        success = True
        return ConversionResponse(
            success=True,
            message="JSON converted to XML successfully",
            output_filename=result_filename,
            download_url=_build_download_url(result_filename),
        )

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError, ValueError, json.JSONDecodeError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in convert_json_to_xml: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during conversion",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path, None if success else output_path)


# ---------------------------------------------------------------------------
# 8. Convert JSON to CSV
# ---------------------------------------------------------------------------

@router.post("/json-to-csv", response_model=ConversionResponse)
async def convert_json_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    delimiter: Optional[str] = Form(","),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Convert JSON to CSV format.
    Supports both direct upload and S3 file key.
    """
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)
        
        # Standardized input handling (Direct Upload or S3)
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
        if filename and filename.strip() and filename.lower() != "string":
            if not filename.lower().endswith('.csv'):
                filename += '.csv'
            output_filename = filename
        else:
            base_name = os.path.splitext(input_filename)[0] if input_filename else "json_to_csv"
            output_filename = f"{base_name}.csv"

        output_path = os.path.join(settings.output_dir, output_filename)
        os.makedirs(settings.output_dir, exist_ok=True)
        
        # Perform conversion
        with open(input_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            
        csv_result = JSONConversionService.json_to_csv(json_data, delimiter=delimiter)
        
        with open(output_path, "w", encoding="utf-8", newline='') as f:
            f.write(csv_result)

        result_filename = os.path.basename(output_path)
        
        # Upload to S3 if configured
        if settings.s3_bucket:
            try:
                s3_key = s3_service.upload_file_to_s3(output_path, result_filename, "outputs")
                if s3_key:
                    logger.info(f"File uploaded to S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to upload output to S3: {e}")

        # Update log on success
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success",
                output_filename=result_filename,
                output_file_type="csv"
            )

        success = True
        return ConversionResponse(
            success=True,
            message="JSON converted to CSV successfully",
            output_filename=result_filename,
            download_url=_build_download_url(result_filename),
        )

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError, ValueError, json.JSONDecodeError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in convert_json_to_csv: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during conversion",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path, None if success else output_path)


# ---------------------------------------------------------------------------
# 9. Convert JSON to Excel
# ---------------------------------------------------------------------------

@router.post("/json-to-excel", response_model=ConversionResponse)
async def convert_json_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Convert JSON file to Excel.
    Supports both direct upload and S3 file key.
    """
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)
        
        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "json")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="json-to-excel",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="json",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Determine output filename
        if filename and filename.strip() and filename.lower() != "string":
            if not filename.lower().endswith('.xlsx'):
                filename += '.xlsx'
            output_filename = filename
        else:
            base_name = os.path.splitext(input_filename)[0] if input_filename else "json_to_excel"
            output_filename = f"{base_name}.xlsx"

        output_path = os.path.join(settings.output_dir, output_filename)
        os.makedirs(settings.output_dir, exist_ok=True)
        
        # Perform conversion
        with open(input_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            
        result_path = JSONConversionService.json_to_excel(json_data, filename=output_filename)
        result_filename = os.path.basename(result_path)
        
        # Upload to S3 if configured
        if settings.s3_bucket:
            try:
                s3_key = s3_service.upload_file_to_s3(result_path, result_filename, "outputs")
                if s3_key:
                    logger.info(f"File uploaded to S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to upload output to S3: {e}")

        # Update log on success
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success",
                output_filename=result_filename,
                output_file_type="xlsx"
            )

        success = True
        return ConversionResponse(
            success=True,
            message="JSON converted to Excel successfully",
            output_filename=result_filename,
            download_url=_build_download_url(result_filename),
        )

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError, ValueError, json.JSONDecodeError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in convert_json_to_excel: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during conversion",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path, None if success else output_path)


# ---------------------------------------------------------------------------
# 10. Convert Excel to JSON
# ---------------------------------------------------------------------------

@router.post("/excel-to-json", response_model=ConversionResponse)
async def convert_excel_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Convert Excel file to JSON.
    Supports both direct upload and S3 file key.
    """
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)
        
        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "excel")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="excel-to-json",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="xlsx",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Perform conversion
        result = JSONConversionService.excel_to_json(input_path)
        
        # Determine output filename
        if filename and filename.strip() and filename.lower() != "string":
            if not filename.lower().endswith('.json'):
                filename += '.json'
            output_filename = filename
        else:
            base_name = os.path.splitext(input_filename)[0] if input_filename else "excel_to_json"
            output_filename = f"{base_name}.json"
        
        output_path = os.path.join(settings.output_dir, output_filename)
        os.makedirs(settings.output_dir, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
            
        result_filename = os.path.basename(output_path)
        
        # Upload to S3 if configured
        if settings.s3_bucket:
            try:
                s3_key = s3_service.upload_file_to_s3(output_path, result_filename, "outputs")
                if s3_key:
                    logger.info(f"File uploaded to S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to upload output to S3: {e}")

        # Update log on success
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success",
                output_filename=result_filename,
                output_file_type="json"
            )

        success = True
        return ConversionResponse(
            success=True,
            message="Excel converted to JSON successfully",
            output_filename=result_filename,
            download_url=_build_download_url(result_filename),
        )

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in convert_excel_to_json: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during conversion",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path, None if success else output_path)


# ---------------------------------------------------------------------------
# 11. Convert CSV to JSON
# ---------------------------------------------------------------------------

@router.post("/csv-to-json", response_model=ConversionResponse)
async def convert_csv_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    delimiter: str = Form(","),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Convert CSV file to JSON.
    Supports both direct upload and S3 file key.
    """
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)
        
        # Standardized input handling (Direct Upload or S3)
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

        with open(input_path, "r", encoding="utf-8") as f:
            csv_content = f.read()

        result = JSONConversionService.csv_to_json(csv_content, delimiter)

        # Determine output filename
        if filename and filename.strip() and filename.lower() != "string":
            if not filename.lower().endswith('.json'):
                filename += '.json'
            output_filename = filename
        else:
            base_name = os.path.splitext(input_filename)[0] if input_filename else "csv_to_json"
            output_filename = f"{base_name}.json"

        output_path = os.path.join(settings.output_dir, output_filename)
        os.makedirs(settings.output_dir, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)

        result_filename = os.path.basename(output_path)
        
        # Upload to S3 if configured
        if settings.s3_bucket:
            try:
                s3_key = s3_service.upload_file_to_s3(output_path, result_filename, "outputs")
                if s3_key:
                    logger.info(f"File uploaded to S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to upload output to S3: {e}")

        # Update log on success
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success",
                output_filename=result_filename,
                output_file_type="json"
            )

        success = True
        return ConversionResponse(
            success=True,
            message="CSV converted to JSON successfully",
            output_filename=result_filename,
            download_url=_build_download_url(result_filename),
        )

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in convert_csv_to_json: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during conversion",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path, None if success else output_path)


# ---------------------------------------------------------------------------
# 12. Convert JSON to YAML
# ---------------------------------------------------------------------------

@router.post("/json-to-yaml", response_model=ConversionResponse)
async def convert_json_to_yaml(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Convert JSON file to YAML.
    Supports both direct upload and S3 file key.
    """
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)
        
        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "json")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="json-to-yaml",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="json",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Read and parse JSON
        with open(input_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            
        # Determine output filename
        if filename and filename.strip() and filename.lower() != "string":
            if not filename.lower().endswith('.yaml'):
                filename += '.yaml'
            output_filename = filename
        else:
            base_name = os.path.splitext(input_filename)[0] if input_filename else "json_to_yaml"
            output_filename = f"{base_name}.yaml"
        
        output_path = os.path.join(settings.output_dir, output_filename)
        os.makedirs(settings.output_dir, exist_ok=True)

        # Convert to YAML
        yaml_content = JSONConversionService.json_to_yaml(json_data)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        
        result_filename = os.path.basename(output_path)
        
        # Upload to S3 if configured
        if settings.s3_bucket:
            try:
                s3_key = s3_service.upload_file_to_s3(output_path, result_filename, "outputs")
                if s3_key:
                    logger.info(f"File uploaded to S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to upload output to S3: {e}")

        # Update log on success
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success",
                output_filename=result_filename,
                output_file_type="yaml"
            )

        success = True
        return ConversionResponse(
            success=True,
            message="JSON converted to YAML successfully",
            output_filename=result_filename,
            download_url=_build_download_url(result_filename),
        )

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError, ValueError, json.JSONDecodeError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in convert_json_to_yaml: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during conversion",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path, None if success else output_path)


# ---------------------------------------------------------------------------
# 13. Convert JSON objects to CSV
# ---------------------------------------------------------------------------

@router.post("/json-objects-to-csv", response_model=ConversionResponse)
async def convert_json_objects_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    delimiter: str = Form(","),
    db: Session = Depends(get_db)
):
    """
    Convert JSON file (list of objects) to CSV.
    Supports both direct upload and S3 file key.
    """
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)
        
        # Standardized input handling (Direct Upload or S3)
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

        # Read and parse JSON
        with open(input_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            
        # Determine output filename
        if filename and filename.strip() and filename.lower() != "string":
            if not filename.lower().endswith('.csv'):
                filename += '.csv'
            output_filename = filename
        else:
            base_name = os.path.splitext(input_filename)[0] if input_filename else "json_to_csv"
            output_filename = f"{base_name}.csv"
        
        output_path = os.path.join(settings.output_dir, output_filename)
        os.makedirs(settings.output_dir, exist_ok=True)

        # Convert to CSV
        csv_content = JSONConversionService.json_objects_to_csv(json_data, delimiter=delimiter)

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            f.write(csv_content)
        
        result_filename = os.path.basename(output_path)
        
        # Upload to S3 if configured
        if settings.s3_bucket:
            try:
                s3_key = s3_service.upload_file_to_s3(output_path, result_filename, "outputs")
                if s3_key:
                    logger.info(f"File uploaded to S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to upload output to S3: {e}")

        # Update log on success
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success",
                output_filename=result_filename,
                output_file_type="csv"
            )

        success = True
        return ConversionResponse(
            success=True,
            message="JSON objects converted to CSV successfully",
            output_filename=result_filename,
            download_url=_build_download_url(result_filename),
        )

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError, ValueError, json.JSONDecodeError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in convert_json_objects_to_csv: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during conversion",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path, None if success else output_path)


# ---------------------------------------------------------------------------
# 14. Convert JSON objects to Excel
# ---------------------------------------------------------------------------

@router.post("/json-objects-to-excel", response_model=ConversionResponse)
async def convert_json_objects_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Convert JSON file (list of objects) to Excel.
    Supports both direct upload and S3 file key.
    """
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)
        
        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "json")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="json-objects-to-excel",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="json",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Read and parse JSON
        with open(input_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            
        # Validate it's a list of objects
        if not isinstance(json_data, list):
            raise FileProcessingError("Input must be a list of JSON objects")

        # Determine output filename
        if filename and filename.strip() and filename.lower() != "string":
            if not filename.lower().endswith('.xlsx'):
                filename += '.xlsx'
            output_filename = filename
        else:
            base_name = os.path.splitext(input_filename)[0] if input_filename else "json_to_excel"
            output_filename = f"{base_name}.xlsx"
        
        output_path = os.path.join(settings.output_dir, output_filename)
        os.makedirs(settings.output_dir, exist_ok=True)

        # Convert to Excel
        result_path = JSONConversionService.json_objects_to_excel(json_data, filename=output_filename)
        result_filename = os.path.basename(result_path)
        
        # Upload to S3 if configured
        if settings.s3_bucket:
            try:
                s3_key = s3_service.upload_file_to_s3(result_path, result_filename, "outputs")
                if s3_key:
                    logger.info(f"File uploaded to S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to upload output to S3: {e}")

        # Update log on success
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success",
                output_filename=result_filename,
                output_file_type="xlsx"
            )

        success = True
        return ConversionResponse(
            success=True,
            message="JSON objects converted to Excel successfully",
            output_filename=result_filename,
            download_url=_build_download_url(result_filename),
        )

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError, ValueError, json.JSONDecodeError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in convert_json_objects_to_excel: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during conversion",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path, None if success else output_path)


# ---------------------------------------------------------------------------
# 15. Convert YAML to JSON
# ---------------------------------------------------------------------------

@router.post("/yaml-to-json", response_model=ConversionResponse)
async def convert_yaml_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Convert YAML file to JSON.
    Supports both direct upload and S3 file key.
    """
    input_path = None
    output_path = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)
        
        # Standardized input handling (Direct Upload or S3)
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, "yaml")
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type="yaml-to-json",
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type="yaml",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            api_endpoint=request.url.path
        )
        log_id = log.id

        # Read YAML content
        with open(input_path, "r", encoding="utf-8") as f:
            yaml_content = f.read()

        # Convert to JSON
        parsed_data = JSONConversionService.yaml_to_json(yaml_content)
        
        # Determine output filename
        if filename and filename.strip() and filename.lower() != "string":
            if not filename.lower().endswith('.json'):
                filename += '.json'
            output_filename = filename
        else:
            base_name = os.path.splitext(input_filename)[0] if input_filename else "yaml_to_json"
            output_filename = f"{base_name}.json"

        output_path = os.path.join(settings.output_dir, output_filename)
        os.makedirs(settings.output_dir, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
        
        result_filename = os.path.basename(output_path)
        
        # Upload to S3 if configured
        if settings.s3_bucket:
            try:
                s3_key = s3_service.upload_file_to_s3(output_path, result_filename, "outputs")
                if s3_key:
                    logger.info(f"File uploaded to S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to upload output to S3: {e}")

        # Update log on success
        if log_id:
            ConversionLogService.update_log_status(
                db=db,
                log_id=log_id,
                status="success",
                output_filename=result_filename,
                output_file_type="json"
            )

        success = True
        return ConversionResponse(
            success=True,
            message="YAML converted to JSON successfully",
            output_filename=result_filename,
            download_url=_build_download_url(result_filename),
        )

    except HTTPException:
        raise
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError, ValueError) as e:
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error in convert_yaml_to_json: {str(e)}")
        if log_id:
            ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred during conversion",
            details={"error": str(e)},
            status_code=500,
        )
    finally:
        _cleanup_files(input_path, None if success else output_path)


# ---------------------------------------------------------------------------
# Download Endpoint
# ---------------------------------------------------------------------------

@router.get("/download/{filename}")
async def download_file(
    filename: str, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Download converted file and clean up both input and output."""
    file_path = os.path.join(settings.output_dir, filename)
    
    # 1. Search for associated S3 keys in conversion log
    s3_input_key = None
    s3_output_key = None
    
    if settings.database_active:
        from app.app_models.user_conversion import UserConversionDetails
        log = db.query(UserConversionDetails).filter(
            UserConversionDetails.output_filename == filename
        ).order_by(UserConversionDetails.created_at.desc()).first()
        
        if log:
            if log.input_filename and (log.input_filename.startswith("uploads/") or log.input_filename.startswith("s3://")):
                 s3_input_key = log.input_filename.replace("s3://", "")
            
            # Output key is typically outputs/filename
            s3_output_key = f"outputs/{filename}"

    # 2. Handle serving the file
    if os.path.exists(file_path):
        # File is local, serve normally
        response = FileService.create_cleanup_response(file_path, filename, background_tasks)
    elif settings.s3_bucket:
        # File not local, try fetching from S3
        s3_key = s3_output_key or f"outputs/{filename}"
        local_tmp_path = os.path.join(settings.output_dir, f"dl_{filename}")
        
        if s3_service.get_file_from_s3(s3_key, local_tmp_path):
            response = FileService.create_cleanup_response(local_tmp_path, filename, background_tasks)
        else:
            raise HTTPException(status_code=404, detail="File not found in local storage or S3")
    else:
        raise HTTPException(status_code=404, detail="File not found")

    # 3. Add background tasks for S3 cleanup if applicable
    if settings.s3_bucket:
        if s3_output_key:
            background_tasks.add_task(s3_service.delete_file, s3_output_key)
        if s3_input_key:
            background_tasks.add_task(s3_service.delete_file, s3_input_key)
            
    return response

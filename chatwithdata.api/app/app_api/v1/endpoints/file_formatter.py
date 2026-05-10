import os
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form, Query, Request, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.app_models.schemas import ConversionResponse
from app.app_services.file_formatter_service import FileFormatterService
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

import shutil
from app.app_core.config import settings

router = APIRouter()

def _determine_output_filename(original_filename: str, provided_filename: Optional[str], target_extension: str) -> str:
    """
    Determine the final output filename.
    """
    target_extension = target_extension.lstrip('.')
    
    if provided_filename and provided_filename.strip():
        filename = provided_filename.strip()
        if not filename.lower().endswith(f".{target_extension}"):
            filename += f".{target_extension}"
        return filename
    
    # Fallback to original filename with new extension
    # specific logic for formatted/minified files to avoid overwrite if same extension
    base_name = os.path.splitext(original_filename)[0]
    
    # If suffix is not already present, we might want to add one if the input/output extension is same
    # But usually custom filename implies user wants that specific name.
    # For auto-generated, we usually append _formatted or _minified in the service, 
    # but here we want to control the final name in the endpoint for consistency.
    
    return f"{base_name}_formatted.{target_extension}"


@router.post("/format-json", response_model=ConversionResponse)
async def format_json(
    request: Request,
    file: UploadFile = File(...),
    indent: int = Form(2),
    sort_keys: bool = Form(False),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Format JSON file with proper indentation and sorting."""
    # Get file info
    file.file.seek(0, 2)
    input_size = file.file.tell()
    file.file.seek(0)

    # Get user_id
    user_id = await get_user_id(request, db)

    # Initial log
    log = ConversionLogService.log_conversion(
        db=db,
        user_id=user_id,
        conversion_type="format-json",
        input_filename=file.filename,
        input_file_size=input_size,
        input_file_type="json",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        api_endpoint=request.url.path
    )

    input_path = None
    
    try:
        FileService.validate_file(file)
        input_path = FileService.save_uploaded_file(file)
        
        output_filename = _determine_output_filename(file.filename, filename, "json")
        # Service returns a temp path usually
        temp_output_path = FileFormatterService.format_json(input_path, indent, sort_keys)
        
        final_output_path = os.path.join(settings.output_dir, output_filename)
        if os.path.abspath(temp_output_path) != os.path.abspath(final_output_path):
             if os.path.exists(final_output_path):
                 os.remove(final_output_path)
             shutil.move(temp_output_path, final_output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log.id,
            status="success",
            output_filename=output_filename,
            output_file_type="json"
        )
        
        # Read the formatted content for preview
        with open(final_output_path, 'r', encoding='utf-8') as f:
            formatted_json = f.read()

        return ConversionResponse(
            success=True,
            message="JSON file formatted successfully",
            output_filename=output_filename,
            download_url=f"/api/v1/fileformattertools/download/{output_filename}",
            details={"formatted_json": formatted_json}
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        if input_path:
            FileFormatterService.cleanup_temp_files(input_path)


@router.post("/validate-json")
async def validate_json(
    request: Request,
    file: UploadFile = File(...),
    schema_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Validate JSON file against schema or basic JSON syntax."""
    # Get file info
    file.file.seek(0, 2)
    input_size = file.file.tell()
    file.file.seek(0)
    
    # Get user_id
    user_id = await get_user_id(request, db)

    # Initial log
    log = ConversionLogService.log_conversion(
        db=db,
        user_id=user_id,
        conversion_type="validate-json",
        input_filename=file.filename,
        input_file_size=input_size,
        input_file_type="json",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        api_endpoint=request.url.path
    )

    input_path = None
    schema_path = None
    
    try:
        # Validate file
        FileService.validate_file(file)
        
        # Save uploaded file
        input_path = FileService.save_uploaded_file(file)
        
        # Save schema file if provided
        if schema_file:
            FileService.validate_file(schema_file)
            schema_path = FileService.save_uploaded_file(schema_file)
        
        # Validate JSON
        validation_result = FileFormatterService.validate_json(input_path, schema_path)
        
        # Update log on success (Note: validation doesn't produce an output file usually, but we mark success)
        ConversionLogService.update_log_status(
            db=db,
            log_id=log.id,
            status="success"
        )

        return {
            "success": True,
            "message": "JSON validation completed",
            "validation_result": validation_result
        }
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        if input_path:
            FileFormatterService.cleanup_temp_files(input_path)
        if schema_path:
            FileFormatterService.cleanup_temp_files(schema_path)


@router.post("/validate-xml")
async def validate_xml(
    request: Request,
    file: UploadFile = File(...),
    xsd_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Validate XML file against XSD schema or basic XML syntax."""
    # Get file info
    file.file.seek(0, 2)
    input_size = file.file.tell()
    file.file.seek(0)
    
    # Get user_id
    user_id = await get_user_id(request, db)

    # Initial log
    log = ConversionLogService.log_conversion(
        db=db,
        user_id=user_id,
        conversion_type="validate-xml",
        input_filename=file.filename,
        input_file_size=input_size,
        input_file_type="xml",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        api_endpoint=request.url.path
    )

    input_path = None
    xsd_path = None
    
    try:
        # Validate file
        FileService.validate_file(file)
        
        # Save uploaded file
        input_path = FileService.save_uploaded_file(file)
        
        # Save XSD file if provided
        if xsd_file:
            FileService.validate_file(xsd_file)
            xsd_path = FileService.save_uploaded_file(xsd_file)
        
        # Validate XML
        validation_result = FileFormatterService.validate_xml(input_path, xsd_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log.id,
            status="success"
        )
        
        return {
            "success": True,
            "message": "XML validation completed",
            "validation_result": validation_result
        }
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        if input_path:
            FileFormatterService.cleanup_temp_files(input_path)
        if xsd_path:
            FileFormatterService.cleanup_temp_files(xsd_path)


@router.post("/validate-xsd")
async def validate_xsd(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Validate XSD schema file."""
    # Get file info
    file.file.seek(0, 2)
    input_size = file.file.tell()
    file.file.seek(0)
    
    # Get user_id
    user_id = await get_user_id(request, db)

    # Initial log
    log = ConversionLogService.log_conversion(
        db=db,
        user_id=user_id,
        conversion_type="validate-xsd",
        input_filename=file.filename,
        input_file_size=input_size,
        input_file_type="xsd",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        api_endpoint=request.url.path
    )

    input_path = None
    
    try:
        # Validate file
        FileService.validate_file(file)
        
        # Save uploaded file
        input_path = FileService.save_uploaded_file(file)
        
        # Validate XSD
        validation_result = FileFormatterService.validate_xsd(input_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log.id,
            status="success"
        )
        
        return {
            "success": True,
            "message": "XSD validation completed",
            "validation_result": validation_result
        }
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        if input_path:
            FileFormatterService.cleanup_temp_files(input_path)


@router.post("/minify-json", response_model=ConversionResponse)
async def minify_json(
    request: Request,
    file: UploadFile = File(...),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Minify JSON file by removing unnecessary whitespace."""
    # Get file info
    file.file.seek(0, 2)
    input_size = file.file.tell()
    file.file.seek(0)
    
    # Get user_id
    user_id = await get_user_id(request, db)

    # Initial log
    log = ConversionLogService.log_conversion(
        db=db,
        user_id=user_id,
        conversion_type="minify-json",
        input_filename=file.filename,
        input_file_size=input_size,
        input_file_type="json",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        api_endpoint=request.url.path
    )

    input_path = None
    
    try:
        FileService.validate_file(file)
        input_path = FileService.save_uploaded_file(file)
        
        # Override default formatter behavior for minification suffix
        if filename:
             output_filename = _determine_output_filename(file.filename, filename, "json")
        else:
             base_name = os.path.splitext(file.filename)[0]
             output_filename = f"{base_name}_minified.json"

        temp_output_path = FileFormatterService.minify_json(input_path)
        
        final_output_path = os.path.join(settings.output_dir, output_filename)
        if os.path.abspath(temp_output_path) != os.path.abspath(final_output_path):
             if os.path.exists(final_output_path):
                 os.remove(final_output_path)
             shutil.move(temp_output_path, final_output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log.id,
            status="success",
            output_filename=output_filename,
            output_file_type="json"
        )
        
        return ConversionResponse(
            success=True,
            message="JSON file minified successfully",
            output_filename=output_filename,
            download_url=f"/api/v1/fileformattertools/download/{output_filename}"
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        if input_path:
            FileFormatterService.cleanup_temp_files(input_path)


@router.post("/format-xml", response_model=ConversionResponse)
async def format_xml(
    request: Request,
    file: UploadFile = File(...),
    indent: int = Form(2),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Format XML file with proper indentation."""
    # Get file info
    file.file.seek(0, 2)
    input_size = file.file.tell()
    file.file.seek(0)
    
    # Get user_id
    user_id = await get_user_id(request, db)

    # Initial log
    log = ConversionLogService.log_conversion(
        db=db,
        user_id=user_id,
        conversion_type="format-xml",
        input_filename=file.filename,
        input_file_size=input_size,
        input_file_type="xml",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        api_endpoint=request.url.path
    )

    input_path = None
    
    try:
        FileService.validate_file(file)
        input_path = FileService.save_uploaded_file(file)
        
        output_filename = _determine_output_filename(file.filename, filename, "xml")
        temp_output_path = FileFormatterService.format_xml(input_path, indent)
        
        final_output_path = os.path.join(settings.output_dir, output_filename)
        if os.path.abspath(temp_output_path) != os.path.abspath(final_output_path):
             if os.path.exists(final_output_path):
                 os.remove(final_output_path)
             shutil.move(temp_output_path, final_output_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log.id,
            status="success",
            output_filename=output_filename,
            output_file_type="xml"
        )
        
        # Read the formatted content for preview
        with open(final_output_path, 'r', encoding='utf-8') as f:
            formatted_xml = f.read()

        return ConversionResponse(
            success=True,
            message="XML file formatted successfully",
            output_filename=output_filename,
            download_url=f"/api/v1/fileformattertools/download/{output_filename}",
            details={"formatted_xml": formatted_xml}
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        if input_path:
            FileFormatterService.cleanup_temp_files(input_path)


@router.post("/json-schema-info")
async def get_json_schema_info(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Get information about JSON structure and schema."""
    # Get file info
    file.file.seek(0, 2)
    input_size = file.file.tell()
    file.file.seek(0)
    
    # Get user_id
    user_id = await get_user_id(request, db)

    # Initial log
    log = ConversionLogService.log_conversion(
        db=db,
        user_id=user_id,
        conversion_type="json-schema-info",
        input_filename=file.filename,
        input_file_size=input_size,
        input_file_type="json",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        api_endpoint=request.url.path
    )

    input_path = None
    
    try:
        # Validate file
        FileService.validate_file(file)
        
        # Save uploaded file
        input_path = FileService.save_uploaded_file(file)
        
        # Get JSON schema info
        schema_info = FileFormatterService.get_json_schema_info(input_path)
        
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log.id,
            status="success"
        )
        
        return {
            "success": True,
            "message": "JSON schema analysis completed",
            "details": {"schema_info": schema_info}
        }
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type=type(e).__name__,
            message=str(e),
            status_code=400
        )
    except Exception as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        raise create_error_response(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(e)},
            status_code=500
        )
    finally:
        # Cleanup temporary files
        if input_path:
            FileFormatterService.cleanup_temp_files(input_path)


@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported input formats."""
    try:
        formats = FileFormatterService.get_supported_formats()
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
    from app.app_core.config import settings
    from app.app_services.file_service import FileService
    import os
    
    file_path = os.path.join(settings.output_dir, filename)
    return FileService.create_cleanup_response(file_path, filename, background_tasks)

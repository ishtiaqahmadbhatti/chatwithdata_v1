import os
import shutil
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form, Query, Request, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.app_models.schemas import ConversionResponse
from app.app_services.office_documents_conversion_service import OfficeDocumentsConversionService
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
    return f"/api/v1/officedocumentsconversiontools/download/{filename}"

async def _read_file_content(file: UploadFile) -> bytes:
    """Read UploadFile content as bytes."""
    return await file.read()

async def _read_file_content_str(file: UploadFile) -> str:
    """Read UploadFile content as string."""
    content = await file.read()
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1")

def _determine_output_filename(filename: Optional[str], file: UploadFile, prefix: str, extension: str) -> str:
    """Determine output filename with fallback logic."""
    if filename and filename.strip() and filename.lower() != "string":
        if not filename.lower().endswith(extension):
            filename += extension
        return filename
    
    base_name = os.path.splitext(file.filename)[0] if file.filename else prefix
    return f"{base_name}{extension}"

async def _handle_office_conversion(
    request: Request,
    db: Session,
    file: Optional[UploadFile] = None,
    file_key: Optional[str] = None,
    output_format: str = "pdf",
    tool_name: str = "office-conversion",
    output_filename: Optional[str] = None,
    **kwargs
) -> ConversionResponse:
    """Helper to handle generic office document conversion."""
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
        if hasattr(OfficeDocumentsConversionService, method_name):
            method = getattr(OfficeDocumentsConversionService, method_name)
            
            # Read content based on tool type
            if tool_name.startswith("json-") or tool_name.startswith("json_"):
                import json
                with open(input_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
            elif tool_name in ["csv-to-excel", "xml-to-csv", "xml-to-excel", "xml-to-json", "srt-to-excel", "srt-to-xlsx", "srt-to-xls", "srt-to-csv", "srt-to-text", "srt-to-json", "srt-to-vtt", "vtt-to-srt", "vtt-to-excel", "vtt-to-xlsx", "vtt-to-xls", "vtt-to-csv", "vtt-to-text", "vtt-to-json"]:
                # These take strings
                with open(input_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            else:
                # Default is bytes
                with open(input_path, "rb") as f:
                    content = f.read()

            # Call method with arguments
            if tool_name == "pdf-to-word":
                 result = method(content, output_filename=final_filename)
            elif tool_name == "excel-to-xml":
                 result = method(content, kwargs.get("root_name", "data"), kwargs.get("record_name", "record"))
            else:
                 result = method(content)
                 
            # Some methods return a path, others return string content
            if isinstance(result, str) and not os.path.exists(result):
                # result is string content
                with open(output_path_final, "w", encoding="utf-8") as out_f:
                    out_f.write(result)
                temp_output_path = output_path_final
            else:
                # result is a path
                temp_output_path = result
        else:
            raise UnsupportedFileTypeError(f"Unsupported tool: {tool_name}")
            
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
            message=f"Document converted to {output_format.upper()} successfully",
            output_filename=final_filename,
            download_url=_build_download_url(final_filename),
            converted_data=result if isinstance(result, str) and not os.path.exists(result) else None
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
# PDF Conversion Endpoints
# ---------------------------------------------------------------------------

@router.post("/pdf-to-csv", response_model=ConversionResponse)
async def convert_pdf_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to CSV."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="csv", 
        tool_name="pdf-to-csv", 
        output_filename=output_filename
    )

@router.post("/pdf-to-excel", response_model=ConversionResponse)
async def convert_pdf_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to Excel."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xlsx", 
        tool_name="pdf-to-excel", 
        output_filename=output_filename
    )

@router.post("/pdf-to-word", response_model=ConversionResponse)
async def convert_pdf_to_word(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to Word."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="docx", 
        tool_name="pdf-to-word", 
        output_filename=output_filename
    )

@router.post("/word-to-pdf", response_model=ConversionResponse)
async def convert_word_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Word to PDF."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="pdf", 
        tool_name="word-to-pdf", 
        output_filename=output_filename
    )

@router.post("/word-to-html", response_model=ConversionResponse)
async def convert_word_to_html(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Word to HTML."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="html", 
        tool_name="word-to-html", 
        output_filename=output_filename
    )

@router.post("/word-to-text", response_model=ConversionResponse)
async def convert_word_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Word to Text."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="txt", 
        tool_name="word-to-text", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# PowerPoint Conversion Endpoints
# ---------------------------------------------------------------------------

@router.post("/powerpoint-to-pdf", response_model=ConversionResponse)
async def convert_powerpoint_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PowerPoint to PDF."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="pdf", 
        tool_name="powerpoint-to-pdf", 
        output_filename=output_filename
    )

@router.post("/powerpoint-to-html", response_model=ConversionResponse)
async def convert_powerpoint_to_html(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PowerPoint to HTML."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="html", 
        tool_name="powerpoint-to-html", 
        output_filename=output_filename
    )

@router.post("/powerpoint-to-text", response_model=ConversionResponse)
async def convert_powerpoint_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PowerPoint to Text."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="txt", 
        tool_name="powerpoint-to-text", 
        output_filename=output_filename
    )

@router.post("/excel-to-pdf", response_model=ConversionResponse)
async def convert_excel_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Excel to PDF."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="pdf", 
        tool_name="excel-to-pdf", 
        output_filename=output_filename
    )

@router.post("/excel-to-xps", response_model=ConversionResponse)
async def convert_excel_to_xps(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Excel to XPS."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xps", 
        tool_name="excel-to-xps", 
        output_filename=output_filename
    )

@router.post("/excel-to-html", response_model=ConversionResponse)
async def convert_excel_to_html(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Excel to HTML."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="html", 
        tool_name="excel-to-html", 
        output_filename=output_filename
    )
@router.post("/excel-to-csv", response_model=ConversionResponse)
async def convert_excel_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Excel to CSV."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="csv", 
        tool_name="excel-to-csv", 
        output_filename=output_filename
    )

@router.post("/excel-to-ods", response_model=ConversionResponse)
async def convert_excel_to_ods(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Excel to ODS."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="ods", 
        tool_name="excel-to-ods", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# ODS Conversion Endpoints
# ---------------------------------------------------------------------------

@router.post("/ods-to-csv", response_model=ConversionResponse)
async def convert_ods_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert ODS to CSV."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="csv", 
        tool_name="ods-to-csv", 
        output_filename=output_filename
    )

@router.post("/ods-to-pdf", response_model=ConversionResponse)
async def convert_ods_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert ODS to PDF."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="pdf", 
        tool_name="ods-to-pdf", 
        output_filename=output_filename
    )

@router.post("/ods-to-excel", response_model=ConversionResponse)
async def convert_ods_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert ODS to Excel."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xlsx", 
        tool_name="ods-to-excel", 
        output_filename=output_filename
    )

@router.post("/csv-to-excel", response_model=ConversionResponse)
async def convert_csv_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert CSV to Excel."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xlsx", 
        tool_name="csv-to-excel", 
        output_filename=output_filename
    )

@router.post("/excel-to-xml", response_model=ConversionResponse)
async def convert_excel_to_xml(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    root_name: str = Form("data"),
    record_name: str = Form("record"),
    db: Session = Depends(get_db)
):
    """Convert Excel to XML."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xml", 
        tool_name="excel-to-xml", 
        output_filename=output_filename,
        root_name=root_name,
        record_name=record_name
    )

@router.post("/xml-to-csv", response_model=ConversionResponse)
async def convert_xml_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert XML to CSV."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="csv", 
        tool_name="xml-to-csv", 
        output_filename=output_filename
    )

@router.post("/xml-to-excel", response_model=ConversionResponse)
async def convert_xml_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert XML to Excel."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xlsx", 
        tool_name="xml-to-excel", 
        output_filename=output_filename
    )

@router.post("/json-to-excel", response_model=ConversionResponse)
async def convert_json_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert JSON to Excel."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xlsx", 
        tool_name="json-to-excel", 
        output_filename=output_filename
    )

@router.post("/excel-to-json", response_model=ConversionResponse)
async def convert_excel_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Excel to JSON."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="json", 
        tool_name="excel-to-json", 
        output_filename=output_filename
    )

@router.post("/json-objects-to-excel", response_model=ConversionResponse)
async def convert_json_objects_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert JSON Objects to Excel."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xlsx", 
        tool_name="json-objects-to-excel", 
        output_filename=output_filename
    )

@router.post("/bson-to-excel", response_model=ConversionResponse)
async def convert_bson_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert BSON to Excel."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xlsx", 
        tool_name="bson-to-excel", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# SRT Conversion Endpoints
# ---------------------------------------------------------------------------

@router.post("/srt-to-excel", response_model=ConversionResponse)
async def convert_srt_to_excel(
    request: Request,
    file: UploadFile = File(...),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT to Excel."""
    
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
        conversion_type="srt-to-excel",
        input_filename=file.filename,
        input_file_size=input_size,
        input_file_type="srt",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        api_endpoint=request.url.path
    )

    try:
        content = await _read_file_content_str(file)
        
        service_output_path = OfficeDocumentsConversionService.srt_to_excel(content)
        
        output_filename = _determine_output_filename(filename, file, "srt_to_excel", ".xlsx")
        output_path = os.path.join(settings.output_dir, output_filename)
        
        if os.path.abspath(service_output_path) != os.path.abspath(output_path):
            shutil.move(service_output_path, output_path)
            
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log.id,
            status="success",
            output_filename=output_filename,
            output_file_type="xlsx"
        )
        
        return ConversionResponse(
            success=True,
            message="SRT converted to Excel successfully",
            output_filename=output_filename,
            download_url=_build_download_url(output_filename)
        )
    except Exception as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        return create_error_response("Failed to convert SRT to Excel", str(e))

@router.post("/srt-to-xlsx", response_model=ConversionResponse)
async def convert_srt_to_xlsx(
    request: Request,
    file: UploadFile = File(...),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT to XLSX."""
    
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
        conversion_type="srt-to-xlsx",
        input_filename=file.filename,
        input_file_size=input_size,
        input_file_type="srt",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        api_endpoint=request.url.path
    )

    try:
        content = await _read_file_content_str(file)
        
        service_output_path = OfficeDocumentsConversionService.srt_to_xlsx(content)
        
        output_filename = _determine_output_filename(filename, file, "srt_to_xlsx", ".xlsx")
        output_path = os.path.join(settings.output_dir, output_filename)
        
        if os.path.abspath(service_output_path) != os.path.abspath(output_path):
            shutil.move(service_output_path, output_path)
            
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log.id,
            status="success",
            output_filename=output_filename,
            output_file_type="xlsx"
        )
        
        return ConversionResponse(
            success=True,
            message="SRT converted to XLSX successfully",
            output_filename=output_filename,
            download_url=_build_download_url(output_filename)
        )
    except Exception as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        return create_error_response("Failed to convert SRT to XLSX", str(e))

@router.post("/srt-to-xls", response_model=ConversionResponse)
async def convert_srt_to_xls(
    request: Request,
    file: UploadFile = File(...),
    filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT to XLS."""
    
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
        conversion_type="srt-to-xls",
        input_filename=file.filename,
        input_file_size=input_size,
        input_file_type="srt",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        api_endpoint=request.url.path
    )

    try:
        content = await _read_file_content_str(file)
        
        service_output_path = OfficeDocumentsConversionService.srt_to_xls(content)
        
        output_filename = _determine_output_filename(filename, file, "srt_to_xls", ".xls")
        output_path = os.path.join(settings.output_dir, output_filename)
        
        if os.path.abspath(service_output_path) != os.path.abspath(output_path):
            shutil.move(service_output_path, output_path)
            
        # Update log on success
        ConversionLogService.update_log_status(
            db=db,
            log_id=log.id,
            status="success",
            output_filename=output_filename,
            output_file_type="xls"
        )
        
        return ConversionResponse(
            success=True,
            message="SRT converted to XLS successfully",
            output_filename=output_filename,
            download_url=_build_download_url(output_filename)
        )
    except Exception as e:
        ConversionLogService.update_log_status(db=db, log_id=log.id, status="failed", error_message=str(e))
        return create_error_response("Failed to convert SRT to XLS", str(e))

@router.post("/excel-to-srt", response_model=ConversionResponse)
async def convert_excel_to_srt(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Excel to SRT subtitle format."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="srt", 
        tool_name="excel-to-srt", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# SRT Conversion Endpoints
# ---------------------------------------------------------------------------

@router.post("/srt-to-excel", response_model=ConversionResponse)
async def convert_srt_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT to Excel."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xlsx", 
        tool_name="srt-to-excel", 
        output_filename=output_filename
    )

@router.post("/srt-to-xlsx", response_model=ConversionResponse)
async def convert_srt_to_xlsx(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT to XLSX."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xlsx", 
        tool_name="srt-to-xlsx", 
        output_filename=output_filename
    )

@router.post("/srt-to-xls", response_model=ConversionResponse)
async def convert_srt_to_xls(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT to XLS."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xls", 
        tool_name="srt-to-xls", 
        output_filename=output_filename
    )

@router.post("/srt-to-csv", response_model=ConversionResponse)
async def convert_srt_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT to CSV."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="csv", 
        tool_name="srt-to-csv", 
        output_filename=output_filename
    )

@router.post("/srt-to-text", response_model=ConversionResponse)
async def convert_srt_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT to Text."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="txt", 
        tool_name="srt-to-text", 
        output_filename=output_filename
    )

@router.post("/srt-to-json", response_model=ConversionResponse)
async def convert_srt_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT to JSON."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="json", 
        tool_name="srt-to-json", 
        output_filename=output_filename
    )

@router.post("/srt-to-vtt", response_model=ConversionResponse)
async def convert_srt_to_vtt(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert SRT to VTT."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="vtt", 
        tool_name="srt-to-vtt", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# VTT Conversion Endpoints
# ---------------------------------------------------------------------------

@router.post("/vtt-to-srt", response_model=ConversionResponse)
async def convert_vtt_to_srt(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert VTT to SRT."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="srt", 
        tool_name="vtt-to-srt", 
        output_filename=output_filename
    )

@router.post("/vtt-to-excel", response_model=ConversionResponse)
async def convert_vtt_to_excel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert VTT to Excel."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xlsx", 
        tool_name="vtt-to-excel", 
        output_filename=output_filename
    )

@router.post("/vtt-to-xlsx", response_model=ConversionResponse)
async def convert_vtt_to_xlsx(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert VTT to XLSX."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xlsx", 
        tool_name="vtt-to-xlsx", 
        output_filename=output_filename
    )

@router.post("/vtt-to-xls", response_model=ConversionResponse)
async def convert_vtt_to_xls(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert VTT to XLS."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="xls", 
        tool_name="vtt-to-xls", 
        output_filename=output_filename
    )

@router.post("/vtt-to-csv", response_model=ConversionResponse)
async def convert_vtt_to_csv(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert VTT to CSV."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="csv", 
        tool_name="vtt-to-csv", 
        output_filename=output_filename
    )

@router.post("/vtt-to-text", response_model=ConversionResponse)
async def convert_vtt_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert VTT to Text."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="txt", 
        tool_name="vtt-to-text", 
        output_filename=output_filename
    )

@router.post("/vtt-to-json", response_model=ConversionResponse)
async def convert_vtt_to_json(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert VTT to JSON."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="json", 
        tool_name="vtt-to-json", 
        output_filename=output_filename
    )

# ---------------------------------------------------------------------------
# Excel to Subtitle Endpoints
# ---------------------------------------------------------------------------

@router.post("/xlsx-to-srt", response_model=ConversionResponse)
async def convert_xlsx_to_srt(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert XLSX to SRT."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="srt", 
        tool_name="xlsx-to-srt", 
        output_filename=output_filename
    )

@router.post("/xls-to-srt", response_model=ConversionResponse)
async def convert_xls_to_srt(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert XLS to SRT."""
    return await _handle_office_conversion(
        request=request, 
        db=db, 
        file=file, 
        file_key=file_key, 
        output_format="srt", 
        tool_name="xls-to-srt", 
        output_filename=output_filename
    )

@router.get("/download/{filename}")
async def download_file(filename: str, background_tasks: BackgroundTasks):
    """Download converted file and clean up."""
    file_path = os.path.join(settings.output_dir, filename)
    return FileService.create_cleanup_response(file_path, filename, background_tasks)

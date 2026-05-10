import os
import uuid
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional, Union
from sqlalchemy.orm import Session
from app.app_core.database import get_db
from app.app_services.conversion_log_service import ConversionLogService
from app.app_api.v1.dependencies import get_user_id
from app.app_models.schemas import ConversionResponse
from app.app_services.markdown_conversion_service import MarkdownConversionService
from app.app_services.file_service import FileService
from app.app_core.config import settings
from app.app_core.exceptions import (
    FileProcessingError,
    UnsupportedFileTypeError,
    FileSizeExceededError,
    create_error_response,
)

logger = logging.getLogger(__name__)
router = APIRouter()

def _build_download_url(filename: str) -> str:
    """Build consistent download url for generated files."""
    return f"/api/v1/markdownconversiontools/download/{filename}"

@router.get("/download/{filename}")
async def download_file(filename: str, background_tasks: BackgroundTasks):
    """Download a converted file and clean up."""
    file_path = os.path.join(settings.output_dir, filename)
    return FileService.create_cleanup_response(file_path, filename, background_tasks)

async def _handle_markdown_conversion(
    request: Request,
    db: Session,
    file: Optional[UploadFile] = None,
    file_key: Optional[str] = None,
    output_format: str = "md",
    tool_name: str = "markdown-conversion",
    output_filename: Optional[str] = None
) -> ConversionResponse:
    """Helper to handle generic markdown conversion."""
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    success = False
    log_id = None
    
    try:
        # Get user_id
        user_id = await get_user_id(request, db)

        # Derive input category from the SOURCE format (the token before '-to-')
        # e.g. "pdf-to-markdown" -> source = "pdf"
        #      "markdown-to-pdf" -> source = "markdown"
        #      "html-to-markdown" -> source = "html" (maps to "document")
        #      "word-to-markdown" -> source = "word"  (maps to "office")
        _source = tool_name.split("-to-")[0] if "-to-" in tool_name else "document"
        _source_category_map = {
            "pdf":      "pdf",
            "markdown": "markdown",
            "html":     "document",
            "word":     "office",
        }
        category = _source_category_map.get(_source, "document")
        input_path, input_filename, input_size = FileService.get_file_input(file, file_key, category)
        
        # Initial log
        log = ConversionLogService.log_conversion(
            db=db,
            user_id=user_id,
            conversion_type=tool_name,
            input_filename=input_filename,
            input_file_size=input_size,
            input_file_type=input_filename.split('.')[-1].lower() if '.' in input_filename else category,
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
        if hasattr(MarkdownConversionService, method_name):
            method = getattr(MarkdownConversionService, method_name)
            
            # Markdown service methods typically take (input_path, output_path)
            result_path = method(input_path, output_path_final)
            output_path = result_path
        else:
            raise UnsupportedFileTypeError(f"Unsupported tool: {tool_name}")
            
        # Update log
        ConversionLogService.update_log_status(
            db=db,
            log_id=log_id,
            status="success",
            output_filename=final_filename,
            output_file_type=output_format.lower()
        )
        
        # Read content if text-based for response
        converted_data = None
        if output_format.lower() in ["md", "html", "txt", "tex"]:
             try:
                 with open(output_path, "r", encoding="utf-8") as f:
                     converted_data = f.read()
             except: pass

        success = True
        return ConversionResponse(
            success=True,
            message=f"Converted to {output_format.upper()} successfully",
            output_filename=final_filename,
            download_url=_build_download_url(final_filename),
            converted_data=converted_data
        )
        
    except (FileProcessingError, UnsupportedFileTypeError, FileSizeExceededError) as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type=type(e).__name__, message=str(e), status_code=400)
    except Exception as e:
        if log_id: ConversionLogService.update_log_status(db=db, log_id=log_id, status="failed", error_message=str(e))
        raise create_error_response(error_type="InternalServerError", message="An unexpected error occurred", details={"error": str(e)}, status_code=500)
    finally:
        FileService.cleanup_files(input_path, None if success else output_path)

# 1. PDF to Markdown
@router.post("/pdf-to-markdown", response_model=ConversionResponse)
async def convert_pdf_to_markdown(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert PDF to Markdown format."""
    return await _handle_markdown_conversion(
        request, db, file, file_key, "md", "pdf-to-markdown", output_filename
    )

# 2. Markdown to PDF
@router.post("/markdown-to-pdf", response_model=ConversionResponse)
async def convert_markdown_to_pdf(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Markdown to PDF format."""
    return await _handle_markdown_conversion(
        request, db, file, file_key, "pdf", "markdown-to-pdf", output_filename
    )

# 3. Markdown to HTML
@router.post("/markdown-to-html", response_model=ConversionResponse)
async def convert_markdown_to_html(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Markdown to HTML format."""
    return await _handle_markdown_conversion(
        request, db, file, file_key, "html", "markdown-to-html", output_filename
    )

# 4. Markdown to ePUB
@router.post("/markdown-to-epub", response_model=ConversionResponse)
async def convert_markdown_to_epub(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Markdown to ePUB format."""
    return await _handle_markdown_conversion(
        request, db, file, file_key, "epub", "markdown-to-epub", output_filename
    )

# 5. Markdown to Word
@router.post("/markdown-to-word", response_model=ConversionResponse)
async def convert_markdown_to_word(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Markdown to Word docx format."""
    return await _handle_markdown_conversion(
        request, db, file, file_key, "docx", "markdown-to-word", output_filename
    )

# 6. Markdown to LaTeX
@router.post("/markdown-to-latex", response_model=ConversionResponse)
async def convert_markdown_to_latex(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Markdown to LaTeX format."""
    return await _handle_markdown_conversion(
        request, db, file, file_key, "tex", "markdown-to-latex", output_filename
    )

# 7. Markdown to Text
@router.post("/markdown-to-text", response_model=ConversionResponse)
async def convert_markdown_to_text(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Markdown to plain text."""
    return await _handle_markdown_conversion(
        request, db, file, file_key, "txt", "markdown-to-text", output_filename
    )

# 8. HTML to Markdown
@router.post("/html-to-markdown", response_model=ConversionResponse)
async def convert_html_to_markdown(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert HTML to Markdown format."""
    return await _handle_markdown_conversion(
        request, db, file, file_key, "md", "html-to-markdown", output_filename
    )

# 9. Word to Markdown
@router.post("/word-to-markdown", response_model=ConversionResponse)
async def convert_word_to_markdown(
    request: Request,
    file: Optional[UploadFile] = File(None),
    file_key: Optional[str] = Form(None),
    output_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Convert Word docx to Markdown format."""
    return await _handle_markdown_conversion(
        request, db, file, file_key, "md", "word-to-markdown", output_filename
    )

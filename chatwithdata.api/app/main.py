import warnings
# Suppress WeasyPrint system-library warning (Cairo/Pango not on Windows - OK on Lambda)
warnings.filterwarnings("ignore", message=".*WeasyPrint.*")
warnings.filterwarnings("ignore", module="weasyprint")
# Suppress requests/urllib3 version mismatch warning
warnings.filterwarnings("ignore", category=Warning, module="requests")
import urllib3
urllib3.disable_warnings()

from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler as fastapi_validation_handler
from app.app_core.config import settings
from app.app_core.exceptions import SmartConvertException
from app.app_core.database import init_db, test_connection, get_db
from sqlalchemy.orm import Session
from app.app_core.middleware import SecurityHeadersMiddleware, LoggingMiddleware
from app.app_api.v1.api import api_router
from app.app_models.request_log import RequestLog
from app.app_services.request_logging_service import (
    ensure_client_id_cookie,
    extract_ip,
    detect_source,
    parse_device_info,
)
import time
import logging
import os
import uuid
from app.app_core.ocr_utils import configure_tesseract

# Configure Tesseract OCR
configure_tesseract()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
# ChatWithData FastAPI - Enterprise File Conversion & Processing Platform

A comprehensive, enterprise-grade file conversion and manipulation platform supporting **20+ conversion types** and **50+ file formats** with advanced processing capabilities.

<details>
<summary><b>🔄 Core Conversion Features</b></summary>

### **PDF Processing & Tools**
- **PDF Conversions**: PDF ↔ Word, Excel, PowerPoint, Images (JPG/PNG), HTML, TXT
- **PDF Manipulation**: Merge, Split, Compress, Rotate, Crop, Watermark, Page Numbers
- **PDF Security**: Password Protection, Unlock, Digital Signing, Redaction
- **PDF Analysis**: OCR Text Extraction, Metadata Extraction, Repair, Compare
- **Advanced PDF**: PDF/A Conversion, Page Extraction, Batch Processing

### **Document Processing**
- **Office Documents**: Word ↔ PDF, Excel ↔ PDF, PowerPoint ↔ PDF
- **Text Formats**: TXT, RTF, Markdown conversions
- **E-book Formats**: EPUB, MOBI, AZW conversions
- **Web Formats**: HTML ↔ PDF, Website Screenshots

### **Media Conversion**
- **Image Processing**: JPG, PNG, GIF, BMP, TIFF, WebP conversions
- **Image Enhancement**: Resize, Compress, Format Conversion, Quality Optimization
- **Video Processing**: MP4, AVI, MOV, MKV format conversions
- **Audio Processing**: MP3, WAV, FLAC, AAC, OGG format conversions

### **Data & Format Conversion**
- **JSON Tools**: JSON ↔ XML, JSON ↔ CSV, JSON Validation, Formatting
- **XML Processing**: XML ↔ JSON, XML ↔ CSV, XML Validation, Transformation
- **CSV Tools**: CSV ↔ Excel, CSV ↔ JSON, CSV Validation, Data Cleaning
- **Subtitle Formats**: SRT, VTT, ASS, SSA subtitle conversions

### **Advanced Processing**
- **OCR Technology**: Text extraction from images and scanned documents
- **File Formatting**: Code formatting, Data validation, Structure optimization
- **Batch Processing**: Multiple file processing, Bulk conversions
- **Website Conversion**: HTML to PDF, Website screenshots, URL processing

</details>

<details>
<summary><b>🛡️ Enterprise Features</b></summary>

### **Security & Authentication**
- **JWT Authentication**: Secure token-based authentication
- **OAuth Integration**: Google, GitHub, Microsoft OAuth support
- **User Management**: Registration, Login, Profile management
- **API Security**: Rate limiting, Request validation, Secure headers

### **Performance & Scalability**
- **High Performance**: Async processing, Optimized algorithms
- **Database Integration**: PostgreSQL with connection pooling
- **File Management**: Secure upload/download, Temporary file cleanup
- **Error Handling**: Comprehensive error management, Detailed logging

### **API & Integration**
- **RESTful API**: Complete REST API with OpenAPI documentation
- **Mobile Support**: Optimized for mobile applications
- **Web Integration**: Angular web application support
- **Developer Tools**: Interactive API docs, ReDoc documentation

</details>

<details>
<summary><b>📊 Technical Specifications</b></summary>

- **Supported Formats**: 50+ file formats across all categories
- **Processing Speed**: Optimized for enterprise workloads
- **File Size Limits**: Configurable size limits for different operations
- **Concurrent Processing**: Multi-threaded file processing
- **Cross-Platform**: Windows, Linux, macOS support

</details>

<details>
<summary><b>🚀 Use Cases</b></summary>

- **Business Document Processing**: Contract conversion, Report generation
- **Media Production**: Video/audio format optimization
- **Data Migration**: Format conversion for system integration
- **Content Management**: Website content processing
- **Educational**: E-book format conversions
- **Development**: Code formatting, Data validation

</details>

---

Built with **FastAPI**, **Python 3.9+**, and modern web technologies for maximum performance and reliability.
""",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add validation error handler to log detailed errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log validation errors in detail for debugging."""
    logger.error(f"Validation error for {request.method} {request.url.path}")
    logger.error(f"Validation errors: {exc.errors()}")
    logger.error(f"Request body: {await request.body()}")
    # Return the default FastAPI validation error response
    return await fastapi_validation_handler(request, exc)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Universal handler for all unhandled exceptions."""
    import traceback
    error_details = traceback.format_exc()
    logger.error(f"Global Exception Handler: {str(exc)}\n{error_details}")
    
    # If it's a known FastAPI/Starlette HTTPException, return its detail
    # This captures the DynamoDB error we raise in UserListService
    if hasattr(exc, "status_code") and hasattr(exc, "detail"):
         return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "error_type": "InternalServerError",
            "message": str(exc),
            "details": error_details if settings.debug else {}
        }
    )

@app.on_event("startup")
async def startup_event():
    """Verify database connections on startup — tables are NOT auto-created here.
    Run scripts/setup_postgresql.py manually to create PostgreSQL tables."""
    logger.info(f"DATABASE_SETTINGS: database_active={settings.database_active}")
    logger.info(f"DYNAMODB_SETTINGS: dynamodb_active={settings.dynamodb_active}, prefix={settings.dynamodb_table_prefix}")

    try:
        # 1. Test PostgreSQL connection if active (no table creation)
        if settings.database_active:
            if test_connection():
                logger.info("PostgreSQL connection successful")
                logger.info("NOTE: Tables are NOT auto-created. Run 'python scripts/setup_postgresql.py' to create them.")
            else:
                logger.error("PostgreSQL connection failed")

        # 2. Check DynamoDB if active
        if settings.dynamodb_active:
            from app.app_services.dynamodb_service import DynamoDBService
            try:
                DynamoDBService.get_resource()
                logger.info(f"DynamoDB Resource initialized in {settings.aws_region}")
            except Exception as e:
                logger.error(f"DYNAMODB CONNECTION FAILED: {e}")
                # Don't crash, allow app to start
    except Exception as e:
        logger.error(f"Initialization error: {e}")



# Start background cleanup task
@app.on_event("startup")
async def start_cleanup_task():
    """Start the background cleanup task on application startup."""
    import threading
    from app.app_services.file_service import FileService
    
    def run_cleanup():
        while True:
            try:
                logger.info("Running scheduled file cleanup...")
                FileService.cleanup_old_files()
            except Exception as e:
                logger.error(f"Error in scheduled cleanup: {e}")
            # Run cleanup every 30 minutes
            # time.sleep(30 * 60)
            # Run cleanup every 1 minute during testing
            time.sleep(30 * 60)
            
    cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
    cleanup_thread.start()
    logger.info("Background cleanup task started")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware for OAuth state/nonce handling
app.add_middleware(SessionMiddleware, secret_key="CHANGE_ME_SUPER_SECRET")

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)


# Custom middleware to handle cases where database is disabled
@app.middleware("http")
async def database_active_middleware(request: Request, call_next):
    # Check if the path needs database and if database is disabled
    # Most auth, user-profile and user-management routes need DB
    db_dependent_paths = ["/api/v1/auth", "/api/v1/userlist", "/api/v1/user-list", "/api/v1/history", "/api/v1/subscription", "/api/v1/guest", "/me", "/update-profile"]
    
    if not settings.database_active and not settings.dynamodb_active:
        is_db_path = any(request.url.path.startswith(path) for path in db_dependent_paths)
        if is_db_path:
            return JSONResponse(
                status_code=503,
                content={
                    "error_type": "DatabaseInactive",
                    "message": "Database related services are currently disabled for maintenance. Please try again later.",
                    "details": {}
                }
            )
            
    response = await call_next(request)
    response.headers["X-Database-Active"] = str(settings.database_active or settings.dynamodb_active)
    return response


# Request logging and timing middleware
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    # Prepare a temporary response to set cookies if needed
    temp_response = JSONResponse({"status": "ok"})
    client_id = ensure_client_id_cookie(request, temp_response)

    request_id = uuid.uuid4().hex
    request.state.client_id = client_id
    request.state.request_id = request_id
    request.state.source = detect_source(request)

    start = time.time()
    response = None
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Error in request_logging_middleware: {e}")
        # Re-raise to let the global exception handler deal with it
        raise e
    finally:
        duration_ms = int((time.time() - start) * 1000)

        # Skip DB logging if both databases are inactive
        if not settings.database_active and not settings.dynamodb_active:
            if response is not None:
                response.headers["X-Process-Time"] = str(duration_ms / 1000.0)
                response.headers["X-Request-Id"] = request_id
            return response

        if response is not None:
            ip, xff = extract_ip(request)
            ua = request.headers.get("user-agent")
            
            # Use RequestLoggingService for dual-database support
            from app.app_services.request_logging_service import RequestLoggingService
            
            # Prepare log data for the service
            RequestLoggingService.log_request(
                client_id=client_id,
                session_id=request.cookies.get("session_id"),
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                query_string=str(request.url.query) if request.url.query else None,
                status_code=response.status_code,
                latency_ms=duration_ms,
                source=request.state.source,
                ip=ip,
                x_forwarded_for=xff,
                user_agent=ua,
                origin=request.headers.get("origin"),
                referer=request.headers.get("referer"),
                device_type=parse_device_info(ua or "")[0],
                os=parse_device_info(ua or "")[1],
                browser=parse_device_info(ua or "")[2],
                app_platform=request.headers.get("x-app-platform"),
                app_version=request.headers.get("x-app-version"),
                device_id=request.headers.get("x-device-id"),
                is_docs=request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"),
                is_download=request.url.path.startswith("/download/"),
            )

            response.headers["X-Process-Time"] = str(duration_ms / 1000.0)
            response.headers["X-Request-Id"] = request_id
            
    # propagate any Set-Cookie from temp_response to the real response
    for k, v in temp_response.raw_headers:
        if k.decode("latin1").lower() == "set-cookie":
            response.raw_headers.append((k, v))

    response.headers["X-Process-Time"] = str(duration_ms / 1000.0)
    response.headers["X-Request-Id"] = request_id
    return response

# Mount static files — wrapped in try/except for Lambda compatibility
# (Lambda read-only fs: /uploads and /assets won't exist unless explicitly created)
import os as _os
_uploads_dir = settings.upload_dir  # /tmp/uploads on Lambda, ./uploads locally
_assets_dir = "assets"

try:
    _os.makedirs(_uploads_dir, exist_ok=True)
    from fastapi.staticfiles import StaticFiles as _SF
    app.mount("/uploads", _SF(directory=_uploads_dir), name="uploads")
except Exception:
    pass  # Uploads directory not available

try:
    if _os.path.isdir(_assets_dir):
        from fastapi.staticfiles import StaticFiles as _SF2
        app.mount("/assets", _SF2(directory=_assets_dir), name="assets")
except Exception:
    pass  # Assets directory not available

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Download endpoint for processed files
@app.get("/download/{filename}")
async def download_file(
    filename: str, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Download processed files and clean up both local and S3."""
    from app.app_services.file_service import FileService
    from app.app_services.s3_service import s3_service
    
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
            if log.input_filename and (log.input_filename.startswith("uploads/")):
                 s3_input_key = log.input_filename
            
            # Output key is typically outputs/filename
            s3_output_key = f"outputs/{filename}"

    # 2. Handle serving the file
    if os.path.exists(file_path):
        response = FileService.create_cleanup_response(file_path, filename, background_tasks)
    elif settings.s3_bucket:
        s3_key = s3_output_key or f"outputs/{filename}"
        local_tmp_path = os.path.join(settings.output_dir, f"dl_{filename}")
        
        if s3_service.get_file_from_s3(s3_key, local_tmp_path):
            response = FileService.create_cleanup_response(local_tmp_path, filename, background_tasks)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    else:
        raise HTTPException(status_code=404, detail="File not found")

    # 3. Add background tasks for S3 cleanup
    if settings.s3_bucket:
        if s3_output_key:
            background_tasks.add_task(s3_service.delete_file, s3_output_key)
        if s3_input_key:
            background_tasks.add_task(s3_service.delete_file, s3_input_key)
            
    return response

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.app_name} 🚀",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health/"
    }

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Provide friendly validation errors for specific endpoints."""
    if request.url.path == "/api/v1/pdfconversiontools/merge":
        return JSONResponse(
            status_code=400,
            content={
                "error_type": "ValidationError",
                "message": "Please select at least 2 PDF files before merging.",
                "details": {"errors": exc.errors()}
            },
        )

    return await fastapi_validation_handler(request, exc)

# Global exception handler
@app.exception_handler(SmartConvertException)
async def smart_convert_exception_handler(request: Request, exc: SmartConvertException):
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=400,
        content={
            "error_type": type(exc).__name__,
            "message": str(exc),
            "details": {}
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

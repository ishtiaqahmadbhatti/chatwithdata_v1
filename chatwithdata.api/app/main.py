import warnings
# Suppress requests/urllib3 version mismatch warning
warnings.filterwarnings("ignore", category=Warning, module="requests")
import urllib3
urllib3.disable_warnings()

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.app_core.config import settings
from app.app_core.exceptions import ChatWithDataException
from app.app_core.middleware import SecurityHeadersMiddleware, LoggingMiddleware
from app.app_api.v1.api import api_router
import time
import logging
import os
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
# ChatWithData FastAPI - YouTube Tools & Agentic RAG Platform

A lightweight FastAPI backend offering comprehensive YouTube data extraction, downloading, and local Agentic RAG services.
""",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Universal handler for all unhandled exceptions."""
    import traceback
    error_details = traceback.format_exc()
    logger.error(f"Global Exception Handler: {str(exc)}\n{error_details}")
    
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
            time.sleep(30 * 60)
            
    cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
    cleanup_thread.start()
    logger.info("Background cleanup task started")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Add security and request logging middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)


# Request timing and metadata middleware
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = uuid.uuid4().hex
    request.state.request_id = request_id

    start = time.time()
    response = None
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Error in request_logging_middleware: {e}")
        raise e
    finally:
        duration_ms = int((time.time() - start) * 1000)
        if response is not None:
            response.headers["X-Process-Time"] = str(duration_ms / 1000.0)
            response.headers["X-Request-Id"] = request_id
            
    return response

# Mount static files — wrapped in try/except for Lambda compatibility
_uploads_dir = settings.upload_dir
try:
    os.makedirs(_uploads_dir, exist_ok=True)
    from fastapi.staticfiles import StaticFiles as _SF
    app.mount("/uploads", _SF(directory=_uploads_dir), name="uploads")
except Exception:
    pass  # Uploads directory not available

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Download endpoint for processed files
@app.get("/download/{filename}")
async def download_file(
    filename: str, 
    background_tasks: BackgroundTasks
):
    """Download processed files and clean up both local and S3."""
    from app.app_services.file_service import FileService
    from app.app_services.s3_service import s3_service
    
    file_path = os.path.join(settings.output_dir, filename)
    
    # Handle serving the file
    if os.path.exists(file_path):
        response = FileService.create_cleanup_response(file_path, filename, background_tasks)
    elif settings.s3_bucket:
        s3_key = f"outputs/{filename}"
        local_tmp_path = os.path.join(settings.output_dir, f"dl_{filename}")
        
        if s3_service.get_file_from_s3(s3_key, local_tmp_path):
            response = FileService.create_cleanup_response(local_tmp_path, filename, background_tasks)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    else:
        raise HTTPException(status_code=404, detail="File not found")

    # Add background tasks for S3 cleanup
    if settings.s3_bucket:
        background_tasks.add_task(s3_service.delete_file, f"outputs/{filename}")
            
    return response

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.app_name} 🚀",
        "version": settings.app_version,
        "docs": "/docs",
    }

# Global exception handler
@app.exception_handler(ChatWithDataException)
async def chat_with_data_exception_handler(request: Request, exc: ChatWithDataException):
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

import os
import re
import uuid
import logging
from typing import Optional, Tuple
from fastapi import UploadFile

logger = logging.getLogger(__name__)
from app.app_core.config import settings
from app.app_core.exceptions import FileSizeExceededError, UnsupportedFileTypeError


class FileService:
    """Service for handling file operations."""
    
    @staticmethod
    def validate_file(file: UploadFile, file_type: str = "general") -> None:
        """Validate uploaded file based on file type."""
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        # if file_size > settings.max_file_size:

        if settings.max_file_size > 0 and file_size > settings.max_file_size:
            raise FileSizeExceededError(
                f"File size {file_size} exceeds maximum allowed size {settings.max_file_size}"
            )
        
        # Define allowed types based on file_type parameter
        if file_type == "video":
            allowed_types = [
                ".mp4", ".mov", ".mkv", ".avi", ".wmv", ".flv", 
                ".webm", ".m4v", ".3gp", ".ogv"
            ]
        elif file_type == "audio":
            allowed_types = [
                ".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma", 
                ".m4a", ".aiff", ".au"
            ]
        elif file_type == "image":
            allowed_types = [
                ".heic", ".avif", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", 
                ".webp", ".svg", ".ico"
            ]
        elif file_type == "jpg":
            allowed_types = [".jpg", ".jpeg"]
        elif file_type == "png":
            allowed_types = [".png"]
        elif file_type == "pdf":
            allowed_types = [".pdf"]
        elif file_type == "document":
            allowed_types = [
                ".srt", ".bson",".json", ".xml", ".csv", ".ods", ".xlsx", ".xls", ".ppt", ".pptx", ".mobi", ".azw", ".azw3", ".fb2", ".fbz", ".epub", ".md", ".markdown", ".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt",
                ".html", ".htm"
            ]
        elif file_type == "xml":
            allowed_types = [".xml"]
        elif file_type == "json":
            allowed_types = [".json"]
        elif file_type == "yaml":
            allowed_types = [".yaml", ".yml"]
        elif file_type == "csv":
            allowed_types = [".csv"]
        elif file_type == "excel":
            allowed_types = [".xlsx", ".xls"]
        elif file_type == "markdown":
            allowed_types = [".md", ".markdown"]
        elif file_type == "office":
            allowed_types = [
                ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", 
                ".odt", ".ods", ".odp"
            ]
        elif file_type == "subtitle":
            allowed_types = [
                ".srt", ".vtt"
            ]
        elif file_type == "epub":
            allowed_types = [".epub"]
        elif file_type == "mobi":
            allowed_types = [".mobi"]
        elif file_type == "azw":
            allowed_types = [".azw"]
        elif file_type == "azw3":
            allowed_types = [".azw3"]
        elif file_type == "fb2":
            allowed_types = [".fb2"]
        elif file_type == "fbz":
            allowed_types = [".fbz"]
        elif file_type == "mov":
            allowed_types = [".mov"]
        elif file_type == "mkv":
            allowed_types = [".mkv"]
        elif file_type == "avi":
            allowed_types = [".avi"]
        elif file_type == "mp4":
            allowed_types = [".mp4"]
        elif file_type == "oxps":
            allowed_types = [".oxps"]
        elif file_type == "ai":
            allowed_types = [".ai"]
        else:  # general/default
            allowed_types = [
                ".bson",".srt", ".vtt", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".bmp", 
                ".tiff", ".docx", ".mp4", ".mov", ".mkv", ".avi", 
                ".mp3", ".wav", ".aac", ".txt", ".json", ".xml", 
                ".csv", ".xlsx", ".xls", ".pptx", ".ppt", ".yaml", ".yml"
            ]
        
        if file.filename:
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_types:
                raise UnsupportedFileTypeError(
                    f"File type {file_ext} is not supported for {file_type} conversion. Allowed types: {allowed_types}"
                )
    
    @staticmethod
    def save_uploaded_file(file: UploadFile) -> str:
        """Save uploaded file and return the file path."""
        # Generate unique filename to avoid conflicts
        filename = file.filename or "unknown_file"
        file_ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(settings.upload_dir, unique_filename)
        
        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)
        
        return file_path
    
    @staticmethod
    def get_output_path(input_path: str, output_extension: str) -> str:
        """Generate output file path."""
        input_filename = os.path.basename(input_path)
        output_filename = os.path.splitext(input_filename)[0] + output_extension
        return os.path.join(settings.output_dir, output_filename)
    


    @staticmethod
    def cleanup_files(*file_paths: Optional[str]) -> None:
        """Remove multiple temporary files."""
        for path in file_paths:
            if path:
                FileService.cleanup_file(path)

    @staticmethod
    def get_file_input(
        file: Optional[UploadFile] = None,
        file_key: Optional[str] = None,
        file_type: str = "general"
    ) -> Tuple[str, str, int]:
        """
        Standardized handler for both direct UploadFile and S3 file_key.
        Returns: (input_path, original_filename, file_size)
        """
        from fastapi import HTTPException
        from app.app_services.s3_service import s3_service
        
        # 1. Clean file_key (ignore placeholders like "string" or "null" from Swagger)
        if file_key and (file_key.lower() in ["string", "null", "none", ""] or file_key == "string"):
            file_key = None

        # 2. Case A: Direct File Upload (Ideal for Development/Testing)
        # If a file is uploaded, we always use it and ignore any file_key provided.
        if file and file.filename:
            logger.info(f"Using direct file upload: {file.filename}")
            # Validate direct upload
            FileService.validate_file(file, file_type)
            
            # Get size
            file.file.seek(0, 2)
            input_size = file.file.tell()
            file.file.seek(0)
            
            # Save locally
            input_path = FileService.save_uploaded_file(file)
            input_filename = file.filename
            return input_path, input_filename, input_size
            
        # 3. Case B: S3 File Key (Used in Production with Pre-signed Uploads)
        # If no direct file is uploaded, look for an S3 storage key.
        elif file_key:
            logger.info(f"Using S3 file retrieval: {file_key}")
            # Check if S3 is actually configured (essential for local dev safety)
            if not settings.s3_bucket:
                 raise HTTPException(
                     status_code=400, 
                     detail="S3 storage is not configured. Please upload the file directly for local testing."
                 )

            # Ensure the upload directory exists
            os.makedirs(settings.upload_dir, exist_ok=True)
            
            # Prepare local path for S3 download
            file_ext = os.path.splitext(file_key)[1].lower() if '.' in file_key else ""
            local_filename = f"s3_{uuid.uuid4()}{file_ext}"
            input_path = os.path.join(settings.upload_dir, local_filename)
            
            # Download from S3
            if not s3_service.get_file_from_s3(file_key, input_path):
                raise HTTPException(status_code=400, detail="Failed to retrieve file from S3 storage. Check if the key exists.")
            
            input_size = os.path.getsize(input_path)
            # Use full key for S3 to help with tracking/cleanup
            input_filename = file_key
            return input_path, input_filename, input_size
        else:
            raise HTTPException(status_code=400, detail="Requirement missing: Either a direct file upload or a storage key is needed.")

    @staticmethod
    def generate_output_path_with_filename(
        filename: str,
        default_extension: str = ".pdf",
        max_base_length: int = 100
    ) -> Tuple[str, str]:
        """Generate a sanitized, unique output path for a given filename."""
        base_name, ext = os.path.splitext(filename or "")

        if not base_name:
            base_name = "merged_document"

        sanitized_base = re.sub(r"[^A-Za-z0-9._-]+", "_", base_name).strip("._")
        if not sanitized_base:
            sanitized_base = "merged_document"

        sanitized_base = sanitized_base[:max_base_length]

        extension = default_extension
        if ext and ext.lower() == default_extension.lower():
            extension = ext.lower()

        if not extension.startswith("."):
            extension = f".{extension}"

        output_dir = settings.output_dir
        os.makedirs(output_dir, exist_ok=True)

        candidate = f"{sanitized_base}{extension}"
        counter = 1
        while os.path.exists(os.path.join(output_dir, candidate)):
            candidate = f"{sanitized_base}_{counter}{extension}"
            counter += 1

        output_path = os.path.join(output_dir, candidate)
        return output_path, candidate
    @staticmethod
    def create_cleanup_response(file_path: str, filename: str, background_tasks: any) -> any:
        """Create a FileResponse that deletes the file after serving."""
        from fastapi.responses import FileResponse
        import os
        
        if not os.path.exists(file_path):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="File not found")
        
        # Add background task to delete the file using our robust cleanup method
        background_tasks.add_task(FileService.cleanup_file, file_path)
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )

    @staticmethod
    def cleanup_old_files() -> None:
        """Remove files from upload and output directories older than the retention period."""
        import time
        from datetime import datetime, timezone, timedelta
        from app.app_core.config import settings
        from app.app_services.s3_service import s3_service
        
        current_time = time.time()
        retention_seconds = settings.file_retention_minutes * 60
        
        # 1. Clean Local Files
        directories = [settings.upload_dir, settings.output_dir]
        for directory in directories:
            if not os.path.exists(directory):
                continue
                
            for filename in os.listdir(directory):
                if filename.startswith('.'):
                    continue
                    
                file_path = os.path.join(directory, filename)
                try:
                    file_modified_time = os.path.getmtime(file_path)
                    if (current_time - file_modified_time) > retention_seconds:
                        FileService.cleanup_file(file_path)
                except Exception:
                    continue

        # 2. Clean S3 Files (if configured)
        if settings.s3_bucket:
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=settings.file_retention_minutes)
            try:
                # Clean uploads and outputs folders in S3
                for folder in ["uploads/", "outputs/"]:
                    old_keys = s3_service.list_objects_older_than(folder, cutoff)
                    if old_keys:
                        s3_service.delete_files(old_keys)
            except Exception as e:
                logger.error(f"Error during S3 scheduled cleanup: {e}")

    @staticmethod
    def cleanup_file(file_path: str) -> bool:
        """Robustly delete a local file, directory, or S3 key with retries."""
        from app.app_services.s3_service import s3_service
        import shutil
        import time
        
        if not file_path:
            return False
            
        # If it looks like an S3 key (e.g. starts with uploads/ or outputs/)
        if file_path.startswith("uploads/") or file_path.startswith("outputs/"):
            return s3_service.delete_file(file_path)

        for attempt in range(3):
            try:
                if os.path.exists(file_path):
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        logger.info(f"Deleted local directory: {file_path}")
                    else:
                        os.remove(file_path)
                        logger.info(f"Deleted local file: {file_path}")
                return True
            except (PermissionError, OSError) as e:
                if attempt == 2:
                    logger.error(f"Error deleting file/directory {file_path}: {e}")
                else:
                    time.sleep(0.2)
            except Exception as e:
                logger.error(f"Error deleting file/directory {file_path}: {e}")
                break
        return False

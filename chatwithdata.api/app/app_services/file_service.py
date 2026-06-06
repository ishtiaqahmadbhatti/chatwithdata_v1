import os
import shutil
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from app.app_core.config import settings

logger = logging.getLogger(__name__)


class FileService:
    """Service for handling file cleanup and response delivery for YouTube downloads."""

    @staticmethod
    def create_cleanup_response(file_path: str, filename: str, background_tasks: any) -> any:
        """Create a FileResponse that schedules the file to be deleted after serving."""
        from fastapi.responses import FileResponse
        
        if not os.path.exists(file_path):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="File not found")
        
        # Add background task to delete the file after response is completed
        background_tasks.add_task(FileService.cleanup_file, file_path)
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )

    @staticmethod
    def cleanup_old_files() -> None:
        """Remove files from output directory older than the retention period (and S3 if active)."""
        current_time = time.time()
        retention_seconds = settings.file_retention_minutes * 60
        
        # 1. Clean Local Output Files
        directory = settings.output_dir
        if os.path.exists(directory):
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
            from app.app_services.s3_service import s3_service
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=settings.file_retention_minutes)
            try:
                # Clean outputs folder in S3 (no uploads tracked)
                old_keys = s3_service.list_objects_older_than("outputs/", cutoff)
                if old_keys:
                    s3_service.delete_files(old_keys)
            except Exception as e:
                logger.error(f"Error during S3 scheduled cleanup: {e}")

    @staticmethod
    def cleanup_file(file_path: str) -> bool:
        """Robustly delete a local file or S3 key with retries."""
        if not file_path:
            return False
            
        # If it looks like an S3 key (e.g. starts with outputs/)
        if file_path.startswith("outputs/"):
            from app.app_services.s3_service import s3_service
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

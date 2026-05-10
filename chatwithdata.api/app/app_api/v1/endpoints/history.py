from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.app_core.database import get_db
from app.app_models.schemas import HistoryListResponse, HistoryItem, UserStatsResponse
from app.app_services.conversion_log_service import ConversionLogService
from app.app_api.v1.dependencies import get_user_id

router = APIRouter()


@router.get("/", response_model=HistoryListResponse)
async def get_history(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Fetch conversion history for the current user with optional filtering."""
    user_id = await get_user_id(request, db)
    if not user_id:
        return HistoryListResponse(success=True, data=[], count=0)
    
    logs = ConversionLogService.get_user_history(
        db, user_id, skip, limit, from_date, to_date, status
    )
    
    history_items = []
    for log in logs:
        # Create dictionary with safe attribute access
        log_data = {
            "id": getattr(log, "id", None),
            "created_at": getattr(log, "created_at", None),
            "conversion_type": getattr(log, "conversion_type", "unknown"),
            "input_filename": getattr(log, "input_filename", "unknown"),
            "input_file_size": getattr(log, "input_file_size", None),
            "input_file_type": getattr(log, "input_file_type", None),
            "output_filename": getattr(log, "output_filename", None),
            "output_file_size": getattr(log, "output_file_size", None),
            "output_file_type": getattr(log, "output_file_type", None),
            "status": getattr(log, "status", "unknown"),
            "error_message": getattr(log, "error_message", None),
        }
        
        # Determine download_url logic
        output_fn = log_data.get("output_filename")
        if output_fn:
             if log_data.get("output_file_type") in ['jpg', 'png', 'tiff', 'svg'] and log_data.get("conversion_type", "").startswith('pdf-to-'):
                  if not "." in output_fn:
                      log_data["download_url"] = f"/download/{output_fn}/"
                  else:
                      log_data["download_url"] = f"/download/{output_fn}"
             else:
                  log_data["download_url"] = f"/download/{output_fn}"
        
        history_items.append(HistoryItem(**log_data))
        
    total_count = ConversionLogService.get_user_history_count(
        db, user_id, from_date, to_date, status
    )
    
    return HistoryListResponse(
        success=True,
        data=history_items,
        count=total_count
    )


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    request: Request,
    db: Session = Depends(get_db)
):
    """Fetch usage statistics for the current user."""
    user_id = await get_user_id(request, db)
    if not user_id:
        return UserStatsResponse(
            success=True,
            files_converted=0,
            data_processed_bytes=0,
            days_active=0
        )
    
    stats = ConversionLogService.get_user_stats(db, user_id)
    return UserStatsResponse(success=True, **stats)

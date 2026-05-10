from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.app_core.database import get_db
from app.app_models.schemas import UserListResponse, SubscriptionUpgrade
from app.app_models.user_list import UserList
from app.app_services.user_list_service import UserListService
from app.app_api.v1.dependencies import get_current_user

router = APIRouter()

@router.post("/upgrade", response_model=UserListResponse)
def upgrade_subscription(
    plan: SubscriptionUpgrade,
    current_user: UserList = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade user subscription plan.
    Requires authentication.
    """
    # Access via enriched properties from service
    if getattr(current_user, "is_premium", False) and getattr(current_user, "subscription_plan", "free") == plan.plan_id:
        return current_user
        
    updated_user = UserListService.upgrade_subscription(db, current_user.id, plan.plan_id)
    if not updated_user:
        raise HTTPException(status_code=400, detail="Failed to upgrade subscription")
        
    return updated_user

@router.get("/status", response_model=UserListResponse)
def get_subscription_status(
    current_user: UserList = Depends(get_current_user)
):
    """
    Get current user subscription status.
    """
    return current_user

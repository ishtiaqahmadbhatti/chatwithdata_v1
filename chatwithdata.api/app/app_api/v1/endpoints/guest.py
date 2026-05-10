from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.app_core.database import get_db
from app.app_models.schemas import UserListResponse, GuestRegistration
from app.app_models.user_list import UserList
from app.app_services.user_list_service import UserListService

router = APIRouter()


@router.post("/register", response_model=UserListResponse, status_code=status.HTTP_201_CREATED)
def register_guest(registration: GuestRegistration, db: Session = Depends(get_db)):
    """
    Register a guest user identifying by device_id.
    If a user with this device_id already exists, return that user.
    """
    
    print(f"DEBUG: register_guest called with device_id={registration.device_id}")
    # Check if user already exists
    user = UserListService.get_user_by_device_id(db, registration.device_id)
    if user:
        print(f"DEBUG: Found existing user for device_id: {user.id}")
        return user
    
    # Create new guest user
    # Create new guest user
    print(f"DEBUG: Creating new guest user for device_id: {registration.device_id}")
    return UserListService.create_guest_user(db, registration.device_id)

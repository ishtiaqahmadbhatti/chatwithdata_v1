from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.app_core.database import get_db
from app.app_models.schemas import UserListCreate, UserListResponse, UserListUpdate
from app.app_services.user_list_service import UserListService

router = APIRouter()

@router.post("/create-user", response_model=UserListResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserListCreate, db: Session = Depends(get_db)):
    """Create a new user in the user list."""
    db_user = UserListService.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return UserListService.create_user(db=db, user=user)

@router.get("/getall-user", response_model=List[UserListResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all users from the user list."""
    users = UserListService.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/getbyid-user/{user_id}", response_model=UserListResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific user by ID."""
    db_user = UserListService.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/update-user/{user_id}", response_model=UserListResponse)
def update_user(user_id: int, user_update: UserListUpdate, db: Session = Depends(get_db)):
    """Update a user's information."""
    db_user = UserListService.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/delete-user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user from the list."""
    success = UserListService.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None

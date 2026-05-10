from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from app.app_core.database import get_db
from app.app_models.user_list import UserList
from app.app_services.auth_service import verify_token, get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserList:
    """Get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(token, credentials_exception)
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserList = Depends(get_current_user)) -> UserList:
    """Get the current active user."""
    # UserList doesn't have is_active, assuming always active for now
    return current_user


async def get_current_admin_user(current_user: UserList = Depends(get_current_active_user)) -> UserList:
    """Get the current admin user."""
    # UserList doesn't have roles yet, so we can't really enforce admin
    return current_user


async def get_current_moderator_user(current_user: UserList = Depends(get_current_active_user)) -> UserList:
    """Get the current moderator user."""
    return current_user


async def get_current_premium_user(current_user: UserList = Depends(get_current_active_user)) -> UserList:
    """Get the current premium user."""
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium access required"
        )
    return current_user


async def get_user_id(request: Request, db: Session) -> Optional[int]:
    """Helper to get user_id from token or device_id header."""
    from app.app_services.user_list_service import UserListService

    # 1. Try Bearer Token
    try:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ")[1]
            from app.app_services.auth_service import verify_token
            try:
                token_data = verify_token(token, None)
                if token_data and token_data.email:
                    user = UserListService.get_user_by_email(db, token_data.email)
                    if user:
                        return user.id
            except Exception:
                pass
    except Exception:
        pass

    # 2. Try Device ID header
    device_id = (
        request.headers.get("x-device-id")
        or request.headers.get("X-Device-Id")
        or request.headers.get("device-id")
    )
    if device_id:
        try:
            user = UserListService.get_user_by_device_id(db, device_id)
            if user:
                return user.id
            else:
                import logging
                logging.getLogger(__name__).warning(f"No user found for device_id: {device_id}")
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error getting user by device_id: {e}")
            pass

    return None
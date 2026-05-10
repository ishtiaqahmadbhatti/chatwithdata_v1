from functools import wraps
from typing import List, Callable, Any
from fastapi import Depends, HTTPException, status
from fastapi import Depends, HTTPException, status
from app.app_models.user_list import UserList
from app.app_api.v1.dependencies import get_current_active_user


def require_roles(*roles: Any):
    """Decorator to require specific roles for endpoint access. (Deprecated for UserList)"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
             # Simplified wrapper that does nothing for now as roles are not supported
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_admin(func: Callable) -> Callable:
    """Decorator to require admin role. (Deprecated)"""
    return require_roles("admin")(func)


def require_moderator(func: Callable) -> Callable:
    """Decorator to require moderator or admin role. (Deprecated)"""
    return require_roles("moderator", "admin")(func)


def require_premium(func: Callable) -> Callable:
    """Decorator to require premium status."""
    # This logic should be handled by dependency but keeping decorator stub
    return require_roles("premium")(func)


def require_verification(func: Callable) -> Callable:
    """Decorator to require verified user. (Deprecated)"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # UserList doesn't have is_verified logic yet
        return await func(*args, **kwargs)
    return wrapper


class PermissionChecker:
    """Class for checking various permissions."""
    
    @staticmethod
    def can_access_conversion(user: UserList, conversion_type: str) -> bool:
        """Check if user can access specific conversion type."""
        # Premium users can access all conversions
        if user.is_premium:
            return True
        
        # Basic users have limited access
        basic_conversions = [
            "pdf-to-word", "word-to-pdf", "image-to-text",
            "jpg-to-pdf", "html-to-pdf"
        ]
        return conversion_type in basic_conversions
    
    @staticmethod
    def can_upload_large_files(user: UserList) -> bool:
        """Check if user can upload large files."""
        # Premium users can upload larger files
        return user.is_premium
    
    @staticmethod
    def get_max_file_size(user: UserList) -> int:
        """Get maximum file size for user."""
        if user.is_premium:
            return 100 * 1024 * 1024  # 100MB
        return 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def get_daily_conversion_limit(user: UserList) -> int:
        """Get daily conversion limit for user."""
        if user.is_premium:
            return 100
        else:
            return 10


def check_conversion_permission(conversion_type: str):
    """Dependency to check conversion permission."""
    def permission_checker(current_user: UserList = Depends(get_current_active_user)):
        if not PermissionChecker.can_access_conversion(current_user, conversion_type):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Premium access required for {conversion_type} conversion"
            )
        return current_user
    return permission_checker


def check_file_size_permission():
    """Dependency to check file size permission."""
    def permission_checker(current_user: UserList = Depends(get_current_active_user)):
        max_size = PermissionChecker.get_max_file_size(current_user)
        return {"user": current_user, "max_file_size": max_size}
    return permission_checker


def check_daily_limit():
    """Dependency to check daily conversion limit."""
    def permission_checker(current_user: UserList = Depends(get_current_active_user)):
        limit = PermissionChecker.get_daily_conversion_limit(current_user)
        return {"user": current_user, "daily_limit": limit}
    return permission_checker

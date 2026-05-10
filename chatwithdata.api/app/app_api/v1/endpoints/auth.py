from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.app_core.database import get_db
from app.app_core.config import settings
from app.app_models.user_list import UserList
from app.app_models.schemas import (
    UserLogin, Token, UserListCreate, UserListResponse, UserListUpdate, ChangePassword, ForgotPassword, VerifyOTP, ResetPasswordConfirm
)
from app.app_services.auth_service import (
    authenticate_user, create_token_pair, 
    refresh_access_token, blacklist_token, get_user_by_email,
    verify_password, get_password_hash
)
from app.app_services.email_service import EmailService
import random
import datetime
import os
import shutil
import time
import string
from app.app_models.otp import PasswordResetOTP
from jose import jwt
from datetime import timedelta
from app.app_services.user_list_service import UserListService
from app.app_services.dynamodb_service import DynamoDBService
from app.app_api.v1.dependencies import get_current_user, get_current_active_user
# from authlib.integrations.starlette_client import OAuth
# from starlette.config import Config
# from starlette.middleware.sessions import SessionMiddleware
import secrets
router = APIRouter()

# OAuth client setup
# OAuth and Social Signup are currently disabled as they rely on the old User model.
# Re-implement using UserList if needed.
# ... (Lines 26-129 commented out effectively)


# Core Authentication Endpoints
# @router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
#     """Register a new user (Deprecated)."""
#     pass


@router.post("/register-userlist", response_model=UserListResponse, status_code=status.HTTP_201_CREATED)
async def register_user_list_endpoint(user_data: UserListCreate, db: Session = Depends(get_db)):
    """Register a new user in the UserList table (specific for mobile task)."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Log incoming data for debugging
    logger.info(f"Registration attempt for email: {user_data.email}")
    logger.debug(f"Registration data: {user_data.model_dump()}")
    
    # Check if user already exists
    if UserListService.get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please Sign In with this email or use another email."
        )
    
    # Create user
    try:
        user = UserListService.create_user(db, user_data)
        logger.info(f"User created successfully: {user.id}")
        return user
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login-userlist", response_model=Token)
async def login_user_list_endpoint(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user from UserList table and return access token."""
    user = UserListService.authenticate(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens (reusing existing system's token creation)
    # Since UserList model doesn't have a 'username', we use 'email' as the sub
    return create_token_pair(user)


# @router.post("/login", response_model=Token)
# async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     # Use /login-userlist instead
#     pass


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    token_data = refresh_access_token(refresh_token, db)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    return Token(**token_data)


@router.post("/logout")
async def logout_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="auth/login"))):
    """Logout user by blacklisting token."""
    success = blacklist_token(token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserListResponse)
async def get_current_user_info(current_user: UserList = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.put("/update-profile", response_model=UserListResponse)
async def update_profile(
    user_update: UserListUpdate,
    current_user: UserList = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile information."""
    return UserListService.update_user(db, user_id=current_user.id, user_update=user_update)


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePassword,
    current_user: UserList = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    # Verify old password
    if not current_user.password or not verify_password(password_data.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # Update Password through service (handles both DBs)
    user_update = UserListUpdate(password=password_data.new_password)
    updated_user = UserListService.update_user(db, current_user.id, user_update)
    
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password."
        )
    
    return {"message": "Password updated successfully"}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    data: ForgotPassword,
    db: Session = Depends(get_db)
):
    """
    Generate 6-digit OTP and send via email.
    """
    print(f"DEBUG: forgot_password for email: {data.email}")
    user = get_user_by_email(db, data.email)
    if not user:
        print(f"DEBUG: No user found for {data.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email address."
        )
    print(f"DEBUG: Found user ID: {user.id}")
    
    # Generate 6-digit OTP
    otp_code = str(random.randint(100000, 999999))
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=3)
    
    # Get user full name (handle None values gracefully)
    first_name = user.first_name if user.first_name else ""
    last_name = user.last_name if user.last_name else ""
    full_name = f"{first_name} {last_name}".strip()
    
    if settings.dynamodb_active:
        otp_data = {
            "email": data.email,
            "otp_code": otp_code,
            "full_name": full_name,
            "device_id": data.device_id,
            "expires_at": expires_at.isoformat(),
            "is_used": False
        }
        print(f"DEBUG: Saving OTP to DynamoDB: {otp_data}")
        success_id = DynamoDBService.log_password_reset_otp(otp_data)
        print(f"DEBUG: OTP Saved with ID: {success_id}")
    else:
        otp_record = PasswordResetOTP(
            email=data.email,
            otp_code=otp_code,
            full_name=full_name,
            device_id=data.device_id,
            expires_at=expires_at,
            is_used=False
        )
        db.add(otp_record)
        db.commit()
        print("DEBUG: OTP Saved to Postgres")
    
    # Send Email
    email_sent = await EmailService.send_otp_email(data.email, otp_code)
    
    if not email_sent:
        print(f"FAILED TO SEND OTP. OTP for {data.email}: {otp_code}")
        return {"message": "OTP generated. Check console if email fails."}
        
    return {"message": "Verification code sent to your email."}


@router.post("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp(
    data: VerifyOTP,
    db: Session = Depends(get_db)
):
    """Verify OTP and return a reset token."""
    print(f"DEBUG: verify_otp for {data.email}, code: {data.otp_code}")
    # Find active, unused OTP
    if settings.dynamodb_active:
        from boto3.dynamodb.conditions import Key, Attr
        # Querying by email GSI
        items = DynamoDBService.query_index(
            "password_reset_otps", 
            "EmailIndex", 
            Key('email').eq(data.email),
            {}
        )
        print(f"DEBUG: Found {len(items)} OTP records in DynamoDB for this email")
        # Filter manually for active/unused/matching code in memory (simplest for this scale)
        now = datetime.datetime.utcnow().isoformat()
        active_otps = [
            i for i in items 
            if i.get('otp_code') == data.otp_code 
            and not i.get('is_used', False) 
            and i.get('expires_at') > now
        ]
        print(f"DEBUG: Filtered to {len(active_otps)} active matching OTPs")
        otp_record = active_otps[0] if active_otps else None
    else:
        otp_record = db.query(PasswordResetOTP).filter(
            PasswordResetOTP.email == data.email,
            PasswordResetOTP.otp_code == data.otp_code,
            PasswordResetOTP.is_used == False,
            PasswordResetOTP.expires_at > datetime.datetime.utcnow()
        ).order_by(PasswordResetOTP.created_at.desc()).first()
    
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )
        
    # Mark as used (optional here, or wait until password reset. 
    # Better to mark verifying as success, but strictly speaking 'used' comes when resetting.
    # However, to prevent re-generation of tokens, we can mark it used.
    # Or just return a token. Let's return a token.
    
    # Create specific reset token
    reset_token_expires = timedelta(minutes=10)
    reset_token = jwt.encode(
        {"sub": data.email, "scope": "reset_password", "exp": datetime.datetime.utcnow() + reset_token_expires},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return {"message": "OTP Verified", "reset_token": reset_token}


@router.post("/reset-password-confirm", status_code=status.HTTP_200_OK)
async def reset_password_confirm(
    data: ResetPasswordConfirm,
    db: Session = Depends(get_db)
):
    """Reset password using the reset token."""
    try:
        payload = jwt.decode(data.reset_token, settings.secret_key, algorithms=[settings.algorithm])
        email = payload.get("sub")
        scope = payload.get("scope")
        if not email or scope != "reset_password":
            raise HTTPException(status_code=400, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
        
    user = get_user_by_email(db, email)
    if not user:
        print(f"DEBUG: Reset Password failed - user {email} not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"DEBUG: Resetting password for user ID: {user.id}")
    # Update Password through service
    user_update = UserListUpdate(password=data.new_password)
    updated_user = UserListService.update_user(db, user.id, user_update)
    
    if updated_user is None:
        print("DEBUG: update_user returned None during password reset")
        raise HTTPException(status_code=500, detail="Failed to reset password")
    
    print("DEBUG: Password reset successful in database")
    
    # Mark OTPs as used
    if settings.dynamodb_active:
        # Get all for email and mark is_used
        from boto3.dynamodb.conditions import Key
        items = DynamoDBService.query_index("password_reset_otps", "EmailIndex", Key('email').eq(email), {})
        for item in items:
            if not item.get('is_used'):
                DynamoDBService.update_item("password_reset_otps", {"id": item['id']}, {"is_used": True})
    else:
        db.query(PasswordResetOTP).filter(
            PasswordResetOTP.email == email,
            PasswordResetOTP.is_used == False
        ).update({"is_used": True})
        db.commit()
    
    return {"message": "Password has been reset successfully."}

    return {"message": "Password has been reset successfully."}


from fastapi import UploadFile, File
import shutil
import os
import uuid

@router.post("/upload-profile-image", response_model=UserListResponse)
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: UserList = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload profile image and update user record with specific path and naming convention."""
    
    # Validation: Ensure only image files are uploaded
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid file type. Only images (JPG, PNG, GIF, etc.) are allowed."
        )

    # Normalize names for path safety
    first = (getattr(current_user, "first_name", "user") or "user").strip().lower().replace(" ", "_")
    last = (getattr(current_user, "last_name", "") or "").strip().lower().replace(" ", "_")
    name_slug = f"{first}_{last}" if last else first
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    timestamp = int(time.time())
    filename = f"{name_slug}{file_extension}"
    
    # Using forward slashes for the database entry consistent with URL standards
    file_key = f"assets/uploads/user_profile_images/{current_user.id}_{name_slug}/{filename}"
    
    try:
        # 1. AWS S3 Upload (if configured)
        if hasattr(settings, "s3_bucket") and settings.s3_bucket:
            import boto3
            import mimetypes
            
            # Default to provided content type, attempt to guess if missing
            content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "image/png"
            
            # Use configured S3 region or fallback to main AWS region
            s3_region = getattr(settings, "s3_region", settings.aws_region)
            
            s3_client = boto3.client('s3', region_name=s3_region)
            
            # Delete old profile images in this directory to keep S3 clean
            prefix = f"assets/uploads/user_profile_images/{current_user.id}_{name_slug}/"
            objects_to_delete = s3_client.list_objects_v2(Bucket=settings.s3_bucket, Prefix=prefix)
            if 'Contents' in objects_to_delete:
                delete_keys = [{'Key': obj['Key']} for obj in objects_to_delete['Contents']]
                s3_client.delete_objects(Bucket=settings.s3_bucket, Delete={'Objects': delete_keys})
                
            s3_client.upload_fileobj(
                file.file,
                settings.s3_bucket,
                file_key,
                ExtraArgs={"ContentType": content_type}
            )
            file_url_base = f"https://{settings.s3_bucket}.s3.{s3_region}.amazonaws.com/{file_key}"
            file_url = f"{file_url_base}?t={timestamp}"
            
        # 2. Local Fallback
        else:
            local_dir = os.path.dirname(file_key)
            if os.path.exists(local_dir):
                shutil.rmtree(local_dir, ignore_errors=True) # Remove old files locally
            os.makedirs(local_dir, exist_ok=True)
            
            local_path = file_key
            with open(local_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file_url = f"{local_path}?t={timestamp}"

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save profile image: {str(e)}"
        )
        
    # Standardize the user update through UserListService (works for both DynamoDB and Postgres)
    user_update = UserListUpdate(profile_image_url=file_url)
    updated_user = UserListService.update_user(db, current_user.id, user_update)
    
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile across the system."
        )
    
    return updated_user


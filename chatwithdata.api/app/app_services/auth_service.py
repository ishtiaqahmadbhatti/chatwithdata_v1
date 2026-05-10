import bcrypt
import logging
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.app_models.user_list import UserList
from app.app_models.schemas import TokenData
from app.app_core.config import settings
import secrets
import redis
import json

logger = logging.getLogger(__name__)

# Password hashing context (Removed)
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

# Redis client for token blacklisting (optional)
try:
    redis_client = redis.Redis(
        host=settings.redis_host, 
        port=settings.redis_port, 
        db=settings.redis_db,
        password=settings.redis_password,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    # Test connection
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception as e:
    logger.debug(f"Redis not available (token blacklisting disabled): {e}")
    REDIS_AVAILABLE = False
    redis_client = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_token_pair(user: Any) -> Dict[str, Any]:
    """Create both access and refresh tokens for a user (supports both User and UserList)."""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # get role if exists, else default
    # role_value = getattr(user.role, 'value', 'user') if hasattr(user, 'role') else 'user'
    role_value = 'user'

    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": role_value},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    # Construct full name
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not full_name:
        full_name = "User"

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "full_name": full_name,
        "profile_image_url": user.profile_image_url if hasattr(user, 'profile_image_url') else None
    }


def verify_token(token: str, credentials_exception, token_type: str = "access"):
    """Verify and decode a JWT token."""
    try:
        # Check if token is blacklisted
        if REDIS_AVAILABLE and is_token_blacklisted(token):
            raise credentials_exception
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type_from_payload: str = payload.get("type")
        
        if email is None or token_type_from_payload != token_type:
            raise credentials_exception
            
        token_data = TokenData(email=email)
        return token_data
    except JWTError:
        raise credentials_exception


def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted."""
    if not REDIS_AVAILABLE:
        return False
    try:
        return redis_client.exists(f"blacklist:{token}")
    except:
        return False


def blacklist_token(token: str) -> bool:
    """Add token to blacklist."""
    if not REDIS_AVAILABLE:
        return False
    try:
        # Get token expiration time
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        exp = payload.get("exp")
        if exp:
            # Set expiration time for blacklist entry
            redis_client.setex(f"blacklist:{token}", int(exp - datetime.utcnow().timestamp()), "1")
        return True
    except:
        return False


def refresh_access_token(refresh_token: str, db: Session) -> Optional[Dict[str, Any]]:
    """Create new access token using refresh token."""
    try:
        # Verify refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if not email or token_type != "refresh":
            return None
            
        # Check if refresh token is blacklisted
        if REDIS_AVAILABLE and is_token_blacklisted(refresh_token):
            return None
            
        if not db:
            return None
            
        # Get user
        user = get_user_by_email(db, email)
        if not user:
            return None
            
        # Create new token pair
        return create_token_pair(user)
        
    except JWTError:
        return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[UserList]:
    """Authenticate a user with email and password."""
    # Use UserListService for consistent logic and subscription attachment
    from app.app_services.user_list_service import UserListService
    return UserListService.authenticate(db, email, password)


def get_user_by_email(db: Session, email: str) -> Optional[UserList]:
    """Get user by email."""
    # Use UserListService for consistent logic and subscription attachment
    from app.app_services.user_list_service import UserListService
    return UserListService.get_user_by_email(db, email)


def get_user_by_username(db: Session, username: str) -> Optional[UserList]:
    """Get user by username. (Assuming email is username)"""
    return get_user_by_email(db, username)


def create_user(db: Session, user_data: dict) -> Optional[UserList]:
    """Create a new user."""
    if not db:
        return None
    hashed_password = get_password_hash(user_data["password"])
    db_user = UserList(
        email=user_data["email"],
        # username=user_data["username"], UserList has no username
        password=hashed_password,
        first_name=user_data.get("first_name", ""),
        last_name=user_data.get("last_name", ""),
        # role=UserRole.USER  # Default role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_role(db: Session, user_id: int, new_role: Any) -> Optional[UserList]:
    """Update user role (admin only)."""
    if not db:
        return None
    # UserList has no role, pass
    return db.query(UserList).filter(UserList.id == user_id).first()


def get_users_by_role(db: Session, role: Any) -> list[UserList]:
    """Get all users with a specific role."""
    # Return all for now or empty?
    return []


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[UserList]:
    """Get all users with pagination."""
    if not db:
        return []
    return db.query(UserList).offset(skip).limit(limit).all()


def update_user_last_login(db: Session, user: UserList):
    """Update user's last login timestamp."""
    # user.last_login = datetime.utcnow()
    # db.commit()
    pass

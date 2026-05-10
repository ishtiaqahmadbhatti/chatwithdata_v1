from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.app_core.config import settings
import logging

logger = logging.getLogger(__name__)

# Lazy initialization of database engine and session
engine = None
SessionLocal = None

def get_engine():
    global engine
    if engine is None:
        if settings.database_active:
            DATABASE_URL = settings.get_database_url
            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=settings.debug
            )
        else:
            # Return a dummy engine or handle it in callers
            return None
    return engine

def get_session_local():
    global SessionLocal
    if SessionLocal is None:
        eng = get_engine()
        if eng:
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=eng)
        else:
            return None
    return SessionLocal

# Create Base class for models
Base = declarative_base()

# Metadata for table operations
metadata = MetaData()


def get_db() -> Session:
    """Dependency to get database session."""
    if not settings.database_active:
        yield None
        return
        
    SessionClass = get_session_local()
    if not SessionClass:
        yield None
        return

    db = SessionClass()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    if not settings.database_active:
        return

    eng = get_engine()
    if not eng:
        return

    try:
        # Import all models here to ensure they are registered
        from app.app_models.request_log import RequestLog
        from app.app_models.user_list import UserList
        from app.app_models.otp import PasswordResetOTP
        
        # Create all tables
        Base.metadata.create_all(bind=eng)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def test_connection():
    """Test database connection."""
    if not settings.database_active:
        return False

    eng = get_engine()
    if not eng:
        return False

    try:
        from sqlalchemy import text
        with eng.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

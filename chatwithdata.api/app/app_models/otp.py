from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.app_core.database import Base
import datetime

class PasswordResetOTP(Base):
    __tablename__ = "smartconverter_password_reset_otps"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    otp_code = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    device_id = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

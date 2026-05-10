from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger
from sqlalchemy.sql import func
from app.app_core.database import Base

class UserConversionDetails(Base):
    """
    Model for logging all user conversion activities.
    Isolated table with no Foreign Keys.
    """
    __tablename__ = "smartconverter_user_conversion_details"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    
    # User Identification (No FK)
    user_id = Column(Integer, nullable=True, index=True)
    
    # Conversion Details
    conversion_type = Column(String(100), nullable=False)
    input_filename = Column(String(500), nullable=False)
    input_file_size = Column(BigInteger, nullable=True) # Bytes
    input_file_type = Column(String(50), nullable=True)
    
    output_filename = Column(String(500), nullable=True)
    output_file_size = Column(BigInteger, nullable=True)
    output_file_type = Column(String(50), nullable=True)
    
    # Status & Error
    status = Column(String(50), default="pending") # pending, success, failed
    error_message = Column(Text, nullable=True)
    
    # Metadata
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    method = Column(String(10), nullable=True) # POST, GET etc.
    api_endpoint = Column(String(200), nullable=True)

    def __repr__(self):
        return f"<UserConversionDetails(id={self.id}, type='{self.conversion_type}', status='{self.status}')>"

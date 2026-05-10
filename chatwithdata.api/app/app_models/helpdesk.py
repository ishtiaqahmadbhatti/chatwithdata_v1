from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.app_core.database import Base

class CustomerContactUsSupport(Base):
    __tablename__ = "smartconverter_customer_contactus_support_details"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())

class CustomerGeneralInquiry(Base):
    __tablename__ = "smartconverter_customer_general_inquiries_details"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    attachment_path = Column(String, nullable=True)
    user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())

class CustomerFAQ(Base):
    __tablename__ = "smartconverter_customer_frequently_asked_questions_details"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    category = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())

class CustomerFeedback(Base):
    __tablename__ = "smartconverter_customer_feedback_details"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    feedback = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())

class CustomerTechnicalSupport(Base):
    __tablename__ = "smartconverter_customer_technical_support_details"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    issue_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    os_info = Column(String, nullable=True) 
    browser_info = Column(String, nullable=True)
    attachment_path = Column(String, nullable=True)
    user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())

class CustomerToolFeedback(Base):
    __tablename__ = "smartconverter_customer_tool_feedback_details"
    id = Column(Integer, primary_key=True, index=True)
    tool_name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    rating = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=True)
    user_email = Column(String, nullable=True)
    user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())

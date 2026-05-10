from sqlalchemy.orm import Session
from app.app_models.helpdesk import (
    CustomerContactUsSupport, CustomerGeneralInquiry, CustomerFAQ,
    CustomerFeedback, CustomerTechnicalSupport, CustomerToolFeedback
)
from app.app_models.schemas import (
    HelpdeskContactUsCreate, HelpdeskGeneralInquiryCreate, HelpdeskFAQCreate,
    HelpdeskFeedbackCreate, HelpdeskTechnicalSupportCreate, HelpdeskToolFeedbackCreate
)
from app.app_services.email_service import EmailService
from app.app_services.dynamodb_service import DynamoDBService
from typing import Optional
from fastapi import UploadFile
import os
import uuid
import shutil

class HelpdeskService:
    @staticmethod
    async def _save_attachment(file: Optional[UploadFile], category: str) -> Optional[str]:
        if not file:
            return None
            
        UPLOAD_DIR = f"assets/uploads/customer_support_documents/{category}"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Use original filename
        filename = file.filename
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return file_path

    @staticmethod
    async def create_contact_us(db: Session, data: HelpdeskContactUsCreate, user_id: Optional[int] = None):
        from app.app_core.config import settings
        db_obj = None
        
        if settings.database_active and db:
            db_obj = CustomerContactUsSupport(
                full_name=data.full_name,
                email=data.email,
                subject=data.subject,
                message=data.message,
                user_id=user_id
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        
        if settings.dynamodb_active:
            DynamoDBService.log_contact_us({
                "full_name": data.full_name,
                "email": data.email,
                "subject": data.subject,
                "message": data.message,
                "user_id": user_id
            })
        
        # Send Email
        html = f"""
        <h2>New Contact Us Message</h2>
        <p><strong>Name:</strong> {data.full_name}</p>
        <p><strong>Email:</strong> {data.email}</p>
        <p><strong>Subject:</strong> {data.subject}</p>
        <p><strong>User ID:</strong> {user_id or 'Guest'}</p>
        <p><strong>Message:</strong></p>
        <p>{data.message}</p>
        """
        await EmailService.send_helpdesk_email(subject=f"Contact Us: {data.subject}", html_content=html)
        return db_obj

    @staticmethod
    async def create_general_inquiry(db: Session, data: HelpdeskGeneralInquiryCreate, file: Optional[UploadFile] = None, user_id: Optional[int] = None):
        attachment_path = await HelpdeskService._save_attachment(file, "general_inquiries")
        from app.app_core.config import settings
        db_obj = None
        
        if settings.database_active and db:
            db_obj = CustomerGeneralInquiry(
                full_name=data.full_name,
                email=data.email,
                subject=data.subject,
                query=data.query,
                attachment_path=attachment_path,
                user_id=user_id
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
        if settings.dynamodb_active:
            DynamoDBService.log_general_inquiry({
                "full_name": data.full_name,
                "email": data.email,
                "subject": data.subject,
                "query": data.query,
                "attachment_path": attachment_path,
                "user_id": user_id
            })
        
        # Send Email
        html = f"""
        <h2>New General Query</h2>
        <p><strong>Name:</strong> {data.full_name}</p>
        <p><strong>Email:</strong> {data.email}</p>
        <p><strong>Subject:</strong> {data.subject}</p>
        <p><strong>User ID:</strong> {user_id or 'Guest'}</p>
        <p><strong>Query:</strong></p>
        <p>{data.query}</p>
        <p><strong>Attachment:</strong> {'Yes' if attachment_path else 'No'}</p>
        """
        attachments = [attachment_path] if attachment_path else None
        await EmailService.send_helpdesk_email(subject=f"Query: {data.subject}", html_content=html, attachments=attachments)
        return db_obj

    @staticmethod
    async def create_faq(db: Session, data: HelpdeskFAQCreate, user_id: Optional[int] = None):
        from app.app_core.config import settings
        db_obj = None
        
        if settings.database_active and db:
            db_obj = CustomerFAQ(
                question=data.question,
                category=data.category,
                user_email=data.user_email,
                user_id=user_id
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
        if settings.dynamodb_active:
            DynamoDBService.log_faq({
                "question": data.question,
                "category": data.category,
                "user_email": data.user_email,
                "user_id": user_id
            })
        
        # Send Email
        html = f"""
        <h2>New FAQ Suggestion</h2>
        <p><strong>Question:</strong> {data.question}</p>
        <p><strong>Category:</strong> {data.category}</p>
        <p><strong>User Email:</strong> {data.user_email or 'N/A'}</p>
        <p><strong>User ID:</strong> {user_id or 'Guest'}</p>
        """
        await EmailService.send_helpdesk_email(subject=f"FAQ Suggestion: {data.question[:30]}...", html_content=html)
        return db_obj

    @staticmethod
    async def create_feedback(db: Session, data: HelpdeskFeedbackCreate, user_id: Optional[int] = None):
        from app.app_core.config import settings
        db_obj = None
        
        if settings.database_active and db:
            db_obj = CustomerFeedback(
                full_name=data.full_name,
                email=data.email,
                feedback=data.feedback,
                rating=data.rating,
                user_id=user_id
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
        if settings.dynamodb_active:
            DynamoDBService.log_feedback({
                "full_name": data.full_name,
                "email": data.email,
                "feedback": data.feedback,
                "rating": data.rating,
                "user_id": user_id
            })
        
        # Send Email
        html = f"""
        <h2>New Customer Feedback</h2>
        <p><strong>Name:</strong> {data.full_name or 'Anonymous'}</p>
        <p><strong>Email:</strong> {data.email or 'N/A'}</p>
        <p><strong>Rating:</strong> {data.rating or 'N/A'}</p>
        <p><strong>User ID:</strong> {user_id or 'Guest'}</p>
        <p><strong>Feedback:</strong></p>
        <p>{data.feedback}</p>
        """
        await EmailService.send_helpdesk_email(subject=f"Customer Feedback", html_content=html)
        return db_obj

    @staticmethod
    async def create_technical_support(db: Session, data: HelpdeskTechnicalSupportCreate, file: Optional[UploadFile] = None, user_id: Optional[int] = None):
        attachment_path = await HelpdeskService._save_attachment(file, "technical_support")
        from app.app_core.config import settings
        db_obj = None
        
        if settings.database_active and db:
            db_obj = CustomerTechnicalSupport(
                full_name=data.full_name,
                email=data.email,
                issue_type=data.issue_type,
                description=data.description,
                os_info=data.os_info,
                browser_info=data.browser_info,
                attachment_path=attachment_path,
                user_id=user_id
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
        if settings.dynamodb_active:
            DynamoDBService.log_technical_support({
                "full_name": data.full_name,
                "email": data.email,
                "issue_type": data.issue_type,
                "description": data.description,
                "os_info": data.os_info,
                "browser_info": data.browser_info,
                "attachment_path": attachment_path,
                "user_id": user_id
            })
        
        # Send Email
        html = f"""
        <h2>New Technical Support Request</h2>
        <p><strong>Name:</strong> {data.full_name}</p>
        <p><strong>Email:</strong> {data.email}</p>
        <p><strong>Issue Type:</strong> {data.issue_type}</p>
        <p><strong>OS:</strong> {data.os_info}</p>
        <p><strong>Browser:</strong> {data.browser_info}</p>
        <p><strong>User ID:</strong> {user_id or 'Guest'}</p>
        <p><strong>Description:</strong></p>
        <p>{data.description}</p>
        <p><strong>Attachment:</strong> {'Yes' if attachment_path else 'No'}</p>
        """
        attachments = [attachment_path] if attachment_path else None
        await EmailService.send_helpdesk_email(subject=f"Tech Support: {data.issue_type}", html_content=html, attachments=attachments)
        return db_obj

    @staticmethod
    async def create_tool_feedback(db: Session, data: HelpdeskToolFeedbackCreate, user_id: Optional[int] = None):
        from app.app_core.config import settings
        db_obj = None
        
        if settings.database_active and db:
            db_obj = CustomerToolFeedback(
                tool_name=data.tool_name,
                category=data.category,
                rating=data.rating,
                feedback=data.feedback,
                user_email=data.user_email,
                user_id=user_id
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
        if settings.dynamodb_active:
            DynamoDBService.log_tool_feedback({
                "tool_name": data.tool_name,
                "category": data.category,
                "rating": data.rating,
                "feedback": data.feedback,
                "user_email": data.user_email,
                "user_id": user_id
            })
        
        # Send Email
        html = f"""
        <h2>New Tool Feedback</h2>
        <p><strong>Tool:</strong> {data.tool_name}</p>
        <p><strong>Category:</strong> {data.category}</p>
        <p><strong>Rating:</strong> {data.rating}/5</p>
        <p><strong>User Email:</strong> {data.user_email or 'N/A'}</p>
        <p><strong>User ID:</strong> {user_id or 'Guest'}</p>
        <p><strong>Feedback:</strong></p>
        <p>{data.feedback}</p>
        """
        await EmailService.send_helpdesk_email(subject=f"Tool Feedback: {data.tool_name}", html_content=html)
        return db_obj

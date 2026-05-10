from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.app_core.database import get_db
from app.app_models.schemas import (
    HelpdeskContactUsCreate,
    HelpdeskGeneralInquiryCreate, 
    HelpdeskFAQCreate, 
    HelpdeskFeedbackCreate,
    HelpdeskTechnicalSupportCreate, 
    HelpdeskToolFeedbackCreate
)
from app.app_services.helpdesk_service import HelpdeskService
from app.app_api.v1.dependencies import get_user_id
from typing import Optional

router = APIRouter()


@router.post("/contact-us", status_code=status.HTTP_201_CREATED)
async def contact_us(
    data: HelpdeskContactUsCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Submit a general inquiry (Contact Us Details).
    """
    try:
        user_id = await get_user_id(request, db)
        return await HelpdeskService.create_contact_us(db, data, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-query", status_code=status.HTTP_201_CREATED)
async def submit_query(
    full_name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    query: str = Form(...),
    file: Optional[UploadFile] = File(None),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Submit a specific query with optional attachment (General Inquiries Details).
    """
    try:
        user_id = await get_user_id(request, db)
        data = HelpdeskGeneralInquiryCreate(
            full_name=full_name,
            email=email,
            subject=subject,
            query=query
        )
        return await HelpdeskService.create_general_inquiry(db, data, file, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/faq", status_code=status.HTTP_201_CREATED)
async def faq(
    data: HelpdeskFAQCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Submit to FAQs Details.
    """
    try:
        user_id = await get_user_id(request, db)
        return await HelpdeskService.create_faq(db, data, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/share-feedback", status_code=status.HTTP_201_CREATED)
async def share_feedback(
    data: HelpdeskFeedbackCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Submit share feedback (Feedback Details).
    """
    try:
        user_id = await get_user_id(request, db)
        return await HelpdeskService.create_feedback(db, data, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/technical-support", status_code=status.HTTP_201_CREATED)
async def technical_support(
    full_name: str = Form(...),
    email: str = Form(...),
    issue_type: str = Form(...),
    description: str = Form(...),
    os_info: Optional[str] = Form(None),
    browser_info: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Submit a technical support request (Technical Support Details).
    """
    try:
        user_id = await get_user_id(request, db)
        data = HelpdeskTechnicalSupportCreate(
            full_name=full_name,
            email=email,
            issue_type=issue_type,
            description=description,
            os_info=os_info,
            browser_info=browser_info
        )
        return await HelpdeskService.create_technical_support(db, data, file, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tool-feedback", status_code=status.HTTP_201_CREATED)
async def tool_feedback(
    data: HelpdeskToolFeedbackCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Submit tool feedback (Tool Feedback Details).
    """
    try:
        user_id = await get_user_id(request, db)
        return await HelpdeskService.create_tool_feedback(db, data, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

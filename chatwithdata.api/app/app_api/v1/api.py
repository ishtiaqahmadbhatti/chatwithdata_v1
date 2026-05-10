from fastapi import APIRouter
from app.app_api.v1.endpoints import health, json_conversion, website_conversion, csv_conversion, xml_conversion, office_documents_conversion, image_conversion, ocr_conversion, subtitle_conversion, text_conversion, file_formatter, ebook_conversion, video_conversion, audio_conversion, pdf_conversion, markdown_conversion, user_list, auth, guest, subscription, history, helpdesk, s3_upload, youtube_tools, rag_tools

api_router = APIRouter()

# Primary Conversion Tools (Main Order)
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(pdf_conversion.router, prefix="/pdfconversiontools", tags=["PDF Conversion"])
api_router.include_router(office_documents_conversion.router, prefix="/officedocumentsconversiontools", tags=["Office Documents Conversion"])
api_router.include_router(image_conversion.router, prefix="/imageconversiontools", tags=["Image Conversion"])
api_router.include_router(video_conversion.router, prefix="/videoconversiontools", tags=["Video Conversion"])
api_router.include_router(audio_conversion.router, prefix="/audioconversiontools", tags=["Audio Conversion"])

api_router.include_router(json_conversion.router, prefix="/jsonconversiontools", tags=["JSON Conversion"])
api_router.include_router(xml_conversion.router, prefix="/xmlconversiontools", tags=["XML Conversion"])
api_router.include_router(csv_conversion.router, prefix="/csvconversiontools", tags=["CSV Conversion"])
api_router.include_router(ocr_conversion.router, prefix="/ocrconversiontools", tags=["OCR Conversion"])
api_router.include_router(website_conversion.router, prefix="/websiteconversiontools", tags=["Website Conversion"])
api_router.include_router(subtitle_conversion.router, prefix="/subtitleconversiontools", tags=["Subtitle Conversion"])
api_router.include_router(markdown_conversion.router, prefix="/markdownconversiontools", tags=["Markdown Conversion"])
api_router.include_router(text_conversion.router, prefix="/textconversiontools", tags=["Text Conversion"])
api_router.include_router(ebook_conversion.router, prefix="/ebookconversiontools", tags=["eBook Conversion"])
api_router.include_router(file_formatter.router, prefix="/fileformattertools", tags=["File Formatter"])

api_router.include_router(user_list.router, prefix="/user-list", tags=["User List"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(guest.router, prefix="/guest", tags=["Guest"])
api_router.include_router(subscription.router, prefix="/subscription", tags=["Subscription"])
api_router.include_router(history.router, prefix="/history", tags=["History"])
api_router.include_router(helpdesk.router, prefix="/helpdesk", tags=["Helpdesk"])
api_router.include_router(s3_upload.router, prefix="/s3", tags=["S3 Storage"])
api_router.include_router(youtube_tools.router, prefix="/youtubetools", tags=["YouTube Tools"])
api_router.include_router(rag_tools.router, prefix="/ragtools", tags=["Agentic RAG"])






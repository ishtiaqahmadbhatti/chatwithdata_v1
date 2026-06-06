from fastapi import APIRouter
from app.app_api.v1.endpoints import youtube_tools, rag_tools

api_router = APIRouter()

api_router.include_router(youtube_tools.router, prefix="/youtubetools", tags=["YouTube Tools"])
api_router.include_router(rag_tools.router, prefix="/ragtools", tags=["Agentic RAG"])







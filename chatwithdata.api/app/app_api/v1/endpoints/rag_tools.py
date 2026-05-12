"""
RAG Tools API Endpoints

Endpoints:
  POST /api/v1/ragtools/ingest         — Ingest YouTube video data into FAISS
  POST /api/v1/ragtools/query          — Query a video using Agentic RAG
  GET  /api/v1/ragtools/sessions       — List all ingested video sessions
  DELETE /api/v1/ragtools/sessions/{id} — Delete a session
"""

import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.app_core.database import get_db
from app.app_api.v1.dependencies import get_user_id
from app.app_services.rag_service import ingest_youtube_data, list_sessions, delete_session
from app.app_services.agent_service import run_rag_query
from app.app_core.exceptions import create_error_response

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Request / Response schemas ─────────────────────────────────────────────────

class IngestRequest(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    video_data: Optional[Dict[str, Any]] = None

class QueryRequest(BaseModel):
    video_id: str
    question: str


# ── 1. Ingest ──────────────────────────────────────────────────────────────────

@router.post("/ingest")
async def ingest_video(
    body: IngestRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Ingest YouTube video data into FAISS for RAG queries.

    **Body**: Simply paste the entire JSON response from `/youtubetools/extract-data`.
    """
    try:
        # Support pasting either the entire extraction response OR just the data object
        target_data = body.data if body.data else body.video_data
        
        if not target_data:
            raise ValueError("Missing 'data' or 'video_data' object in the request.")

        result = ingest_youtube_data(target_data)
        return {
            "success": True,
            "message": f"✅ Ingested {result['chunks_ingested']} chunks for '{result['title']}'",
            "video_id": result["video_id"],
            "chunks_ingested": result["chunks_ingested"],
            "collection": result["collection"],
        }
    except ValueError as e:
        raise create_error_response(error_type="ValidationError", message=str(e), status_code=400)
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise create_error_response(
            error_type="IngestionError",
            message="Failed to ingest video data",
            details={"error": str(e)},
            status_code=500
        )


# ── 2. Query ───────────────────────────────────────────────────────────────────

@router.post("/query")
async def query_video(
    body: QueryRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Query a YouTube video using Agentic RAG (LangGraph + Ollama).

    The agent will:
    1. Retrieve relevant chunks from the video's transcript, metadata & comments
    2. Grade relevance of each chunk
    3. Generate an answer (or rewrite the query and retry if needed)

    **Example questions:**
    - "What is the main topic of this video?"
    - "What do people say in the comments?"
    - "Summarize the transcript"
    - "Who is the channel owner?"
    """
    try:
        result = run_rag_query(
            video_id=body.video_id,
            question=body.question,
        )
        return {
            "success": True,
            **result,
        }
    except Exception as e:
        logger.error(f"RAG query error: {e}")
        raise create_error_response(
            error_type="QueryError",
            message="Failed to process query",
            details={"error": str(e)},
            status_code=500
        )


# ── 3. List Sessions ───────────────────────────────────────────────────────────

@router.get("/sessions")
async def get_sessions():
    """List all ingested YouTube video sessions available for RAG queries."""
    sessions = list_sessions()
    return {
        "success": True,
        "sessions": sessions,
        "total": len(sessions),
    }


# ── 4. Delete Session ──────────────────────────────────────────────────────────

@router.delete("/sessions/{video_id}")
async def remove_session(video_id: str):
    """Delete a video's FAISS index to free up space."""
    deleted = delete_session(video_id)
    if deleted:
        return {"success": True, "message": f"Session for video '{video_id}' deleted."}
    raise create_error_response(
        error_type="NotFound",
        message=f"Session for video '{video_id}' not found.",
        status_code=404
    )

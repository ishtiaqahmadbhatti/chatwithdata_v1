"""
RAG Service — Handles document ingestion and retrieval using FAISS.
Uses Ollama embeddings (qwen3-embedding) and stores per-video indices on disk.
"""

import logging
import os
import shutil
from typing import List, Dict, Any, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.app_core.config import settings

logger = logging.getLogger(__name__)

# ── Helpers ────────────────────────────────────────────────────────────────────

def _faiss_dir() -> str:
    return settings.faiss_persist_dir

def _video_dir(video_id: str) -> str:
    """Directory where a specific video's FAISS index is saved."""
    return os.path.join(_faiss_dir(), f"yt_{video_id}")

def _get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=settings.ollama_embed_model,
        base_url=settings.ollama_base_url,
    )

# ── Text splitter ──────────────────────────────────────────────────────────────
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ".", " ", ""],
)

# ──────────────────────────────────────────────────────────────────────────────
# DOCUMENT BUILDER
# ──────────────────────────────────────────────────────────────────────────────

def _youtube_data_to_documents(video_data: Dict[str, Any]) -> List[Document]:
    """
    Convert structured YouTube data dict into LangChain Documents.
    Each chunk gets metadata so retrieval results are explainable.
    """
    docs: List[Document] = []
    video_id = video_data.get("video_id", "unknown")
    meta_base = {
        "video_id": video_id,
        "url": video_data.get("url", ""),
        "title": video_data.get("metadata", {}).get("title", ""),
    }

    # 1. Metadata block
    m = video_data.get("metadata", {})
    meta_text_parts = []
    if m.get("title"):        meta_text_parts.append(f"Title: {m['title']}")
    if m.get("channel"):      meta_text_parts.append(f"Channel: {m['channel']}")
    if m.get("description"):  meta_text_parts.append(f"Description:\n{m['description']}")
    if m.get("tags"):         meta_text_parts.append(f"Tags: {', '.join(m['tags'])}")
    if m.get("categories"):   meta_text_parts.append(f"Categories: {', '.join(m['categories'])}")
    if m.get("view_count"):   meta_text_parts.append(f"Views: {m['view_count']:,}")
    if m.get("like_count"):   meta_text_parts.append(f"Likes: {m['like_count']:,}")
    if m.get("upload_date"):  meta_text_parts.append(f"Upload Date: {m['upload_date']}")

    if meta_text_parts:
        docs.extend(_splitter.create_documents(
            ["\n".join(meta_text_parts)],
            metadatas=[{**meta_base, "source": "metadata"}]
        ))

    # 2. Transcript (most important — split into chunks)
    transcript = video_data.get("transcript")
    if transcript and transcript.get("full_text"):
        lang = transcript.get("language", "unknown")
        docs.extend(_splitter.create_documents(
            [transcript["full_text"]],
            metadatas=[{**meta_base, "source": "transcript", "language": lang}]
        ))

    # 3. Comments — combine and split
    comments = video_data.get("comments", [])
    if comments:
        comment_lines = []
        for c in comments:
            text   = c.get("text", "").strip()
            author = c.get("author", "Anonymous")
            likes  = c.get("like_count", 0)
            if text:
                comment_lines.append(f"[{author} | 👍{likes}]: {text}")
                
                # Include nested replies if they exist
                replies = c.get("replies", [])
                for r in replies:
                    r_text   = r.get("text", "").strip()
                    r_author = r.get("author", "Anonymous")
                    r_likes  = r.get("like_count", 0)
                    if r_text:
                        comment_lines.append(f"  └─ [{r_author} | 👍{r_likes}]: {r_text}")

        if comment_lines:
            docs.extend(_splitter.create_documents(
                ["\n".join(comment_lines)],
                metadatas=[{**meta_base, "source": "comments"}]
            ))

    logger.info(
        f"Built {len(docs)} chunks for video {video_id} "
        f"(metadata + transcript + {len(comments)} comments)"
    )
    return docs


# ──────────────────────────────────────────────────────────────────────────────
# INGESTION
# ──────────────────────────────────────────────────────────────────────────────

def ingest_youtube_data(video_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest YouTube video data into FAISS.
    Creates (or overwrites) a per-video local index.
    """
    video_id = video_data.get("video_id")
    if not video_id:
        raise ValueError("video_data must contain 'video_id'")

    documents = _youtube_data_to_documents(video_data)
    if not documents:
        raise ValueError("No content found to ingest (transcript, metadata, or comments are all empty).")

    v_dir = _video_dir(video_id)
    embeddings = _get_embeddings()

    # Delete existing index directory for a fresh ingest
    if os.path.exists(v_dir):
        shutil.rmtree(v_dir)
        logger.info(f"Deleted existing FAISS index at: {v_dir}")

    # Build FAISS index in memory
    vectorstore = FAISS.from_documents(
        documents=documents,
        embedding=embeddings
    )
    
    # Save to disk
    vectorstore.save_local(v_dir)

    logger.info(f"Ingested {len(documents)} chunks into FAISS index at '{v_dir}'")
    return {
        "video_id":       video_id,
        "collection":     v_dir,
        "chunks_ingested": len(documents),
        "title":          video_data.get("metadata", {}).get("title", ""),
    }


# ──────────────────────────────────────────────────────────────────────────────
# RETRIEVAL
# ──────────────────────────────────────────────────────────────────────────────

def get_retriever(video_id: str, k: int = 6):
    """Return a LangChain retriever for a given video's FAISS index."""
    v_dir = _video_dir(video_id)
    if not os.path.exists(v_dir):
        raise ValueError(f"No ingested data found for video_id: {video_id}")
        
    vectorstore = FAISS.load_local(
        folder_path=v_dir,
        embeddings=_get_embeddings(),
        allow_dangerous_deserialization=True # Required by LangChain to load local FAISS .pkl files
    )
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": k})


def list_sessions() -> List[Dict[str, Any]]:
    """List all ingested video sessions from FAISS directory."""
    try:
        base_dir = _faiss_dir()
        if not os.path.exists(base_dir):
            return []
            
        sessions = []
        for d in os.listdir(base_dir):
            if d.startswith("yt_"):
                video_id = d[3:]
                # We can't easily get the chunk count without loading the whole index into memory
                # So we'll just say the session exists
                sessions.append({
                    "video_id":   video_id,
                    "collection": d,
                    "status":     "available",
                })
        return sessions
    except Exception as e:
        logger.error(f"Error listing FAISS sessions: {e}")
        return []


def delete_session(video_id: str) -> bool:
    """Delete a video's FAISS index directory."""
    try:
        v_dir = _video_dir(video_id)
        if os.path.exists(v_dir):
            shutil.rmtree(v_dir)
            logger.info(f"Deleted FAISS session for video {video_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting session {video_id}: {e}")
        return False

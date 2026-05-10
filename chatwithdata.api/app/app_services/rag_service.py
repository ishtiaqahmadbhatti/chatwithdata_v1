"""
RAG Service — Handles document ingestion and retrieval from ChromaDB.
Uses Ollama embeddings (qwen3-embedding) and stores per-video collections.
"""

import logging
import os
from typing import List, Dict, Any, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.app_core.config import settings

logger = logging.getLogger(__name__)

# ── Helpers ────────────────────────────────────────────────────────────────────

def _chroma_dir() -> str:
    return settings.chroma_persist_dir

def _get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=settings.ollama_embed_model,
        base_url=settings.ollama_base_url,
    )

def _collection_name(video_id: str) -> str:
    """ChromaDB collection name per video (max 63 chars, alphanumeric + underscore)."""
    return f"yt_{video_id}"

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
    Ingest YouTube video data into ChromaDB.
    Creates (or overwrites) a per-video collection.
    """
    video_id = video_data.get("video_id")
    if not video_id:
        raise ValueError("video_data must contain 'video_id'")

    documents = _youtube_data_to_documents(video_data)
    if not documents:
        raise ValueError("No content found to ingest (transcript, metadata, or comments are all empty).")

    collection = _collection_name(video_id)
    chroma_dir = _chroma_dir()
    embeddings = _get_embeddings()

    # Delete existing collection for a fresh ingest
    try:
        import chromadb
        client = chromadb.PersistentClient(path=chroma_dir)
        existing = [c.name for c in client.list_collections()]
        if collection in existing:
            client.delete_collection(collection)
            logger.info(f"Deleted existing ChromaDB collection: {collection}")
    except Exception as e:
        logger.warning(f"Could not clean existing collection: {e}")

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=collection,
        persist_directory=chroma_dir,
    )

    logger.info(f"Ingested {len(documents)} chunks into ChromaDB collection '{collection}'")
    return {
        "video_id":       video_id,
        "collection":     collection,
        "chunks_ingested": len(documents),
        "title":          video_data.get("metadata", {}).get("title", ""),
    }


# ──────────────────────────────────────────────────────────────────────────────
# RETRIEVAL
# ──────────────────────────────────────────────────────────────────────────────

def get_retriever(video_id: str, k: int = 6):
    """Return a LangChain retriever for a given video's ChromaDB collection."""
    vectorstore = Chroma(
        collection_name=_collection_name(video_id),
        embedding_function=_get_embeddings(),
        persist_directory=_chroma_dir(),
    )
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": k})


def list_sessions() -> List[Dict[str, Any]]:
    """List all ingested video sessions from ChromaDB."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=_chroma_dir())
        sessions = []
        for col in client.list_collections():
            if col.name.startswith("yt_"):
                video_id = col.name[3:]
                sessions.append({
                    "video_id":   video_id,
                    "collection": col.name,
                    "chunks":     col.count(),
                })
        return sessions
    except Exception as e:
        logger.error(f"Error listing ChromaDB sessions: {e}")
        return []


def delete_session(video_id: str) -> bool:
    """Delete a video's ChromaDB collection."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=_chroma_dir())
        client.delete_collection(_collection_name(video_id))
        logger.info(f"Deleted ChromaDB session for video {video_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting session {video_id}: {e}")
        return False

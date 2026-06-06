#!/usr/bin/env python3
"""
Startup script for ChatWithData FastAPI (YouTube Tools & RAG ONLY)
"""

import sys
import os
import warnings
import logging

# Fix for Protobuf descriptor error (often triggered by ChromaDB or Google API)
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Suppress all Python-level warnings globally
warnings.filterwarnings("ignore")

# Silence noisy third-party loggers
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def start_app():
    """Start the FastAPI application with hot-reload enabled."""
    try:
        import uvicorn

        print("Starting ChatWithData FastAPI (YouTube & RAG ONLY)...")
        print("=" * 60)
        print(f"Python executable: {sys.executable}")
        print("Available endpoints:")
        print("- Main API Gateway:    http://127.0.0.1:8001/")
        print("- API Documentation:   http://127.0.0.1:8001/docs")
        print("- ReDoc Documentation: http://127.0.0.1:8001/redoc")
        print("\nFeatures active:")
        print("- YouTube Tools:       /api/v1/youtubetools/")
        print("- Agentic RAG Search:  /api/v1/ragtools/")
        print("=" * 60)
        print("🔥 Hot Reload: ENABLED — changes auto-apply on file save")
        print("Press Ctrl+C to stop the server")
        print("=" * 60)

        # reload=True requires the app to be passed as a STRING "module:attr"
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8001,
            log_level="info",
            reload=True,                          # ← Hot reload on every .py file save
            reload_dirs=["app"],                  # ← Only watch the app/ directory
            reload_excludes=["*.pyc", "__pycache__", "uploads", "outputs", "faiss_db"],
        )

    except Exception as e:
        print(f"Error starting application: {e}")
        return False

    return True


if __name__ == "__main__":
    start_app()

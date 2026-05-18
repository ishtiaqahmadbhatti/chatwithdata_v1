#!/usr/bin/env python3
"""
Startup script for Smart Converter FastAPI
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
logging.getLogger("weasyprint").setLevel(logging.CRITICAL)
logging.getLogger("fontTools").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def start_app():
    """Start the FastAPI application with hot-reload enabled."""
    try:
        import uvicorn

        print("Starting Smart Converter FastAPI...")
        print("=" * 50)
        print(f"Python executable: {sys.executable}")
        print("Available endpoints:")
        print("- Main API: http://192.168.100.12:8001/")
        print("- API Documentation: http://192.168.100.12:8001/docs")
        print("- ReDoc Documentation: http://192.168.100.12:8001/redoc")
        print("- Health Check: http://192.168.100.12:8001/api/v1/health/")
        print("\nFor mobile device access:")
        print("- Physical Device: http://192.168.100.12:8001/")
        print("- Android Emulator: http://10.0.2.2:8001/ (from app)")
        print("- Mobile Docs: http://192.168.100.12:8001/docs")
        print("=" * 50)
        print("\nPDF Conversion Tools available at: /api/v1/pdfconversiontools/")
        print("General Conversion Tools available at: /api/v1/convert/")
        print("\n🔥 Hot Reload: ENABLED — changes auto-apply on file save")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)

        # NOTE: reload=True requires the app to be passed as a STRING "module:attr"
        # NOT as an imported object — uvicorn needs to re-import it in worker processes.
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8001,
            log_level="info",
            reload=True,                          # ← Hot reload on every .py file save
            reload_dirs=["app"],                  # ← Only watch the app/ directory
            reload_excludes=["*.pyc", "__pycache__", "uploads", "outputs"],
        )

    except Exception as e:
        print(f"Error starting application: {e}")
        return False

    return True


if __name__ == "__main__":
    start_app()

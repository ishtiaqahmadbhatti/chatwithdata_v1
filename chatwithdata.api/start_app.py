#!/usr/bin/env python3
"""
Startup script for Smart Converter FastAPI
"""

import sys
import os
import warnings
import logging

# Suppress all Python-level warnings globally
warnings.filterwarnings("ignore")

# Silence noisy third-party loggers
logging.getLogger("weasyprint").setLevel(logging.CRITICAL)
logging.getLogger("fontTools").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# Suppress WeasyPrint C-level stderr (it bypasses Python's sys.stderr)
# We redirect fd=2 (stderr) to devnull briefly during the import phase
import ctypes, io

class _StderrSuppressor:
    """Context manager that suppresses C-level stderr output."""
    def __enter__(self):
        self._devnull = open(os.devnull, 'w')
        self._old_stderr_fd = os.dup(2)
        os.dup2(self._devnull.fileno(), 2)
        return self
    def __exit__(self, *args):
        os.dup2(self._old_stderr_fd, 2)
        os.close(self._old_stderr_fd)
        self._devnull.close()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def start_app():
    """Start the FastAPI application."""
    try:
        # Import app inside stderr suppressor to silence WeasyPrint C-level warnings
        with _StderrSuppressor():
            from app.main import app
        import uvicorn

        print("Starting Smart Converter FastAPI...")
        print("=" * 50)
        print(f"Python executable: {sys.executable}")
        print("Available endpoints:")
        print("- Main API: http://192.168.100.12:8000/")
        print("- API Documentation: http://192.168.100.12:8000/docs")
        print("- ReDoc Documentation: http://192.168.100.12:8000/redoc")
        print("- Health Check: http://192.168.100.12:8000/api/v1/health/")
        print("\nFor mobile device access:")
        print("- Physical Device: http://192.168.100.12:8000/")
        print("- Android Emulator: http://10.0.2.2:8000/ (from app)")
        print("- Mobile Docs: http://192.168.100.12:8000/docs")
        print("=" * 50)
        print("\nPDF Conversion Tools available at: /api/v1/pdfconversiontools/")
        print("General Conversion Tools available at: /api/v1/convert/")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)

        # Start the server
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        
    except Exception as e:
        print(f"Error starting application: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_app()

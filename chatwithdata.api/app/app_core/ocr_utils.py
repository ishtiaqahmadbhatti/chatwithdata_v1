import os
import logging
import pytesseract

logger = logging.getLogger(__name__)

def configure_tesseract():
    """Configure Tesseract OCR path, especially on Windows."""
    if os.name == 'nt':  # Windows
        # Common Tesseract installation paths on Windows
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            os.path.join(os.environ.get('USERPROFILE', ''), r'AppData\Local\Tesseract-OCR\tesseract.exe')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract path configured: {path}")
                return True
        
        logger.warning("Tesseract executable not found in common Windows locations.")
        return False
    else:
        # On Linux/macOS/Lambda
        # 1. First check if it's already in PATH
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            pass
            
        # 2. Check common Linux/Lambda paths
        possible_linux_paths = [
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
            '/opt/bin/tesseract',  # Common path in AWS Lambda Layers
            '/var/task/bin/tesseract' # Another common Lambda path
        ]
        
        for path in possible_linux_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract path configured (Linux/Lambda): {path}")
                return True
        
        logger.warning("Tesseract not found in PATH or common Linux/Lambda locations.")
        return False

def get_poppler_path():
    """Get Poppler path for PDF to Image conversion."""
    if os.name == 'nt':  # Windows
        # Check common Poppler locations
        # User might have poppler in the project root or a specific tools directory
        possible_paths = [
            r'C:\Program Files\poppler\Library\bin',
            r'C:\poppler\Library\bin',
            os.path.join(os.getcwd(), 'tools', 'poppler', 'Library', 'bin')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
    
    # On Linux/Lambda, it's typically in the PATH
    return None # None means it will use system PATH

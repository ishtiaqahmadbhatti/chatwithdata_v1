import os
import json
import base64
import io
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image, ImageOps
import cv2
import numpy as np
from pdf2image import convert_from_path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import cairosvg
try:
    from wand.image import Image as WandImage
    from wand.color import Color
    WAND_AVAILABLE = True
except ImportError:
    WAND_AVAILABLE = False
    WandImage = None
    Color = None
import requests
from bs4 import BeautifulSoup
import pandas as pd
from app.app_core.exceptions import FileProcessingError
from app.app_services.file_service import FileService
from app.app_services.request_logging_service import RequestLoggingService
from app.app_core.ocr_utils import configure_tesseract, get_poppler_path
import logging

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIF_AVAILABLE = True
except ImportError:
    HEIF_AVAILABLE = False

logger = logging.getLogger(__name__)


class ImageConversionService:
    """Service for handling image conversions and transformations."""
    
    # Supported input formats
    SUPPORTED_INPUT_FORMATS = {
        'AVIF', 'WEBP', 'PNG', 'JPG', 'JPEG', 'TIFF', 'SVG', 'HEIC', 'PGM', 'PPM', 
        'GIF', 'BMP', 'YUV', 'PAM', 'AI', 'PDF'
    }
    
    # Supported output formats
    SUPPORTED_OUTPUT_FORMATS = {
        'AVIF', 'WEBP', 'PNG', 'JPG', 'JPEG', 'TIFF', 'SVG', 'HEIC', 'PGM', 'PPM',
        'GIF', 'BMP', 'YUV', 'PAM'
    }
    
    @staticmethod
    def convert_image_format(input_path: str, output_format: str, quality: int = 95) -> str:
        """Convert image from one format to another."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input image file not found: {input_path}")
            
            # Get file extension without dot
            output_format = output_format.upper().replace('.', '')
            if output_format not in ImageConversionService.SUPPORTED_OUTPUT_FORMATS:
                raise FileProcessingError(f"Unsupported output format: {output_format}")
            
            # Generate output path
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = FileService.get_output_path(input_path, f".{output_format.lower()}")
            
            # Handle special formats
            if output_format == 'HEIC':
                return ImageConversionService._convert_to_heic(input_path, output_path)
            elif output_format == 'SVG':
                return ImageConversionService._convert_to_svg(input_path, output_path)
            elif output_format == 'YUV':
                return ImageConversionService._convert_to_yuv(input_path, output_path)
            elif output_format in ['PGM', 'PPM', 'PAM']:
                return ImageConversionService._convert_to_netpbm(input_path, output_path, output_format)
            else:
                # Handle SVG input files natively with cairosvg
                input_ext = os.path.splitext(input_path)[1].upper()
                if input_ext == '.SVG':
                    # Convert SVG to PNG in memory first, since PIL cannot open SVGs
                    import cairosvg
                    png_data = cairosvg.svg2png(url=input_path)
                    img = Image.open(io.BytesIO(png_data))
                else:
                    # Standard PIL conversion for all other formats
                    try:
                        img = Image.open(input_path)
                    except Exception as e:
                        if input_ext in ['.HEIC', '.HEIF']:
                            if not HEIF_AVAILABLE:
                                raise FileProcessingError("HEIC/HEIF support is not enabled. Please install 'pillow-heif' on the server.")
                        raise e
                
                with img:
                    # Convert to RGB if necessary for JPEG
                    if output_format in ['JPG', 'JPEG'] and img.mode in ['RGBA', 'LA', 'P']:
                        # Use a white background for transparent SVGs/PNGs converting to JPG
                        if img.mode in ['RGBA', 'LA']:
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[-1]) # 3 is the alpha channel
                            img = background
                        else:
                            img = img.convert('RGB')
                    
                    # Save with appropriate format and quality
                    save_kwargs = {}
                    if output_format in ['JPG', 'JPEG', 'WEBP']:
                        save_kwargs['quality'] = quality
                        save_kwargs['optimize'] = True
                    elif output_format == 'PNG':
                        save_kwargs['optimize'] = True
                    
                    # Pillow expects 'JPEG', not 'JPG'
                    pil_format = 'JPEG' if output_format == 'JPG' else output_format
                    img.save(output_path, format=pil_format, **save_kwargs)
            
            if not os.path.exists(output_path):
                raise FileProcessingError("Conversion completed but output file was not created")
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"Image format conversion failed: {str(e)}")
    
    @staticmethod
    def image_to_json(input_path: str, output_path: str = None) -> str:
        """Convert image to JSON format with advanced OCR text extraction."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input image file not found: {input_path}")
            
            # Generate output path if not provided
            if output_path is None:
                output_path = FileService.get_output_path(input_path, ".json")
            
            with Image.open(input_path) as img:
                # Extract text using OCR (pytesseract)
                try:
                    import pytesseract
                    
                    # Configure tesseract path
                    configure_tesseract()
                    
                    # Get full extracted text
                    extracted_text = pytesseract.image_to_string(img)
                    
                    # Get detailed OCR data for structured extraction
                    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                    
                    # Organize text by lines and paragraphs
                    lines = []
                    current_line = []
                    current_line_num = -1
                    
                    for i in range(len(ocr_data['text'])):
                        text = ocr_data['text'][i].strip()
                        if text:
                            line_num = ocr_data['line_num'][i]
                            
                            # New line detected
                            if line_num != current_line_num:
                                if current_line:
                                    lines.append({
                                        "line_number": current_line_num,
                                        "text": " ".join([w["text"] for w in current_line]),
                                        "confidence": sum([w["confidence"] for w in current_line]) / len(current_line)
                                    })
                                current_line = []
                                current_line_num = line_num
                            
                            current_line.append({
                                "text": text,
                                "confidence": float(ocr_data['conf'][i])
                            })
                    
                    # Add last line
                    if current_line:
                        lines.append({
                            "line_number": current_line_num,
                            "text": " ".join([w["text"] for w in current_line]),
                            "confidence": sum([w["confidence"] for w in current_line]) / len(current_line)
                        })
                    
                    # Group lines into paragraphs (lines separated by significant vertical gaps)
                    paragraphs = []
                    current_paragraph = []
                    
                    for line in lines:
                        if line["text"].strip():
                            current_paragraph.append(line["text"])
                        elif current_paragraph:
                            paragraphs.append(" ".join(current_paragraph))
                            current_paragraph = []
                    
                    if current_paragraph:
                        paragraphs.append(" ".join(current_paragraph))
                    
                    # Create clean, structured JSON focused on content
                    json_data = {
                        "content": {
                            "full_text": extracted_text.strip(),
                            "paragraphs": paragraphs,
                            "lines": [line["text"] for line in lines],
                            "total_lines": len(lines)
                        },
                        "structure": {
                            "lines_detail": [
                                {
                                    "line": i + 1,
                                    "text": line["text"],
                                    "confidence": round(line["confidence"], 2)
                                }
                                for i, line in enumerate(lines)
                            ]
                        }
                    }
                    
                except ImportError:
                    json_data = {
                        "error": "OCR not available",
                        "message": "pytesseract is not installed or tesseract.exe not found. Please install Tesseract OCR to extract text from images.",
                        "content": {
                            "full_text": "",
                            "paragraphs": [],
                            "lines": []
                        }
                    }
                except Exception as e:
                    json_data = {
                        "error": "OCR extraction failed",
                        "message": str(e),
                        "content": {
                            "full_text": "",
                            "paragraphs": [],
                            "lines": []
                        }
                    }
            
            # Save JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"Image to JSON conversion failed: {str(e)}")
    
    @staticmethod
    def image_to_pdf(input_path: str, page_size: str = 'A4') -> str:
        """Convert image to PDF."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input image file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".pdf")
            
            # Convert image to PDF using img2pdf
            import img2pdf
            
            with open(input_path, "rb") as f:
                img_data = f.read()
            
            # Convert to PDF
            pdf_data = img2pdf.convert(img_data)
            
            # Save PDF
            with open(output_path, "wb") as f:
                f.write(pdf_data)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"Image to PDF conversion failed: {str(e)}")
    
    @staticmethod
    def website_to_image(url: str, output_format: str = 'PNG', width: int = 1920, height: int = 1080) -> str:
        """Convert website to image using Selenium."""
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'--window-size={width},{height}')
            
            # Setup Chrome driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                # Navigate to URL
                driver.get(url)
                
                # Wait for page to load
                driver.implicitly_wait(10)
                
                # Take screenshot
                screenshot = driver.get_screenshot_as_png()
                
                # Generate output path
                safe_url = url.replace('://', '_').replace('/', '_').replace('.', '_')
                output_path = FileService.get_output_path(f"website_{safe_url}", f".{output_format.lower()}")
                
                # Save image
                with Image.open(io.BytesIO(screenshot)) as img:
                    img.save(output_path, format=output_format.upper())
                
                return output_path
                
            finally:
                driver.quit()
                
        except Exception as e:
            raise FileProcessingError(f"Website to image conversion failed: {str(e)}")
    
    @staticmethod
    def html_to_image(html_content: str, output_format: str = 'PNG', width: int = 1920, height: int = 1080) -> str:
        """Convert HTML content to image."""
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'--window-size={width},{height}')
            
            # Setup Chrome driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                # Load HTML content
                driver.get(f"data:text/html;charset=utf-8,{html_content}")
                
                # Wait for content to load
                driver.implicitly_wait(5)
                
                # Take screenshot
                screenshot = driver.get_screenshot_as_png()
                
                # Generate output path
                output_path = FileService.get_output_path("html_content", f".{output_format.lower()}")
                
                # Save image
                with Image.open(io.BytesIO(screenshot)) as img:
                    img.save(output_path, format=output_format.upper())
                
                return output_path
                
            finally:
                driver.quit()
                
        except Exception as e:
            raise FileProcessingError(f"HTML to image conversion failed: {str(e)}")
    
    @staticmethod
    def pdf_to_image(input_path: str, output_format: str = 'PNG', dpi: int = 300, page_number: int = 1) -> str:
        """Convert PDF page to image."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input PDF file not found: {input_path}")
            
            # Convert PDF to images
            images = convert_from_path(input_path, dpi=dpi, first_page=page_number, last_page=page_number, poppler_path=get_poppler_path())
            
            if not images:
                raise FileProcessingError("No pages found in PDF")
            
            # Get the first (and only) page
            image = images[0]
            
            # Generate output path
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = FileService.get_output_path(f"{base_name}_page_{page_number}", f".{output_format.lower()}")
            
            # Save image
            image.save(output_path, format=output_format.upper())
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"PDF to image conversion failed: {str(e)}")
    
    @staticmethod
    def pdf_to_tiff(input_path: str, dpi: int = 300, page_number: int = 1) -> str:
        """Convert PDF page to TIFF."""
        return ImageConversionService.pdf_to_image(input_path, 'TIFF', dpi, page_number)
    
    @staticmethod
    def pdf_to_svg(input_path: str, dpi: int = 300, page_number: int = 1) -> str:
        """Convert PDF page to SVG."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input PDF file not found: {input_path}")
            
            # Convert PDF to images first
            images = convert_from_path(input_path, dpi=dpi, first_page=page_number, last_page=page_number, poppler_path=get_poppler_path())
            
            if not images:
                raise FileProcessingError("No pages found in PDF")
            
            # Get the first (and only) page
            image = images[0]
            
            # Generate output path
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = FileService.get_output_path(f"{base_name}_page_{page_number}", ".svg")
            
            # Convert to SVG
            return ImageConversionService._convert_to_svg_from_pil(image, output_path)
            
        except Exception as e:
            raise FileProcessingError(f"PDF to SVG conversion failed: {str(e)}")
    
    @staticmethod
    def ai_to_svg(input_path: str) -> str:
        """Convert AI (Adobe Illustrator) file to SVG."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input AI file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".svg")
            
            # Attempt 1: Try Pillow (requires Ghostscript for EPS-like AI)
            try:
                with Image.open(input_path) as img:
                    # Force load to ensure it's readable
                    img.load()
                    return ImageConversionService._convert_to_svg_from_pil(img, output_path)
            except Exception as pil_error:
                # Pillow failed (likely no Ghostscript or not EPS-compatible)
                pass

            # Attempt 2: Try pdf2image (requires Poppler, works for PDF-compatible AI)
            try:
                # AI files are often valid PDFs
                images = convert_from_path(input_path, first_page=1, last_page=1, poppler_path=get_poppler_path())
                if images:
                    return ImageConversionService._convert_to_svg_from_pil(images[0], output_path)
            except Exception as pdf_error:
                pass
            
            # Attempt 3: Try PyMuPDF (fitz) - Robust, self-contained PDF/AI handler
            try:
                import fitz
                doc = fitz.open(input_path)
                if doc.page_count > 0:
                    page = doc.load_page(0)
                    svg_content = page.get_svg_image()
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(svg_content)
                    return output_path
            except Exception as fitz_error:
                # Log detailed error for debugging if needed
                logger.warning(f"PyMuPDF failed for AI conversion: {fitz_error}")
                pass
            
            # If all fail
            raise FileProcessingError("Could not convert .ai file. Ensure it is PDF-compatible or Ghostscript is installed.")
            
        except Exception as e:
            raise FileProcessingError(f"AI to SVG conversion failed: {str(e)}")
    
    @staticmethod
    def remove_exif_data(input_path: str) -> str:
        """Remove EXIF data from image."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input image file not found: {input_path}")
            
            # Generate output path
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = FileService.get_output_path(f"{base_name}_no_exif", os.path.splitext(input_path)[1])
            
            with Image.open(input_path) as img:
                # Create a new image without EXIF data
                data = list(img.getdata())
                image_without_exif = Image.new(img.mode, img.size)
                image_without_exif.putdata(data)
                
                # Save without EXIF
                image_without_exif.save(output_path, format=img.format)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"EXIF data removal failed: {str(e)}")
    
    @staticmethod
    def _convert_to_svg_from_pil(pil_image, output_path: str) -> str:
        """Convert PIL image to SVG format."""
        try:
            # Convert to RGB if necessary
            if pil_image.mode in ['RGBA', 'LA', 'P']:
                pil_image = pil_image.convert('RGB')
            
            # Create SVG content
            width, height = pil_image.size
            
            # Convert image to base64
            img_buffer = io.BytesIO()
            pil_image.save(img_buffer, format='PNG')
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <image href="data:image/png;base64,{img_base64}" 
           width="{width}" height="{height}"/>
</svg>'''
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"SVG conversion failed: {str(e)}")
    
    @staticmethod
    def _convert_to_heic(input_path: str, output_path: str) -> str:
        """Convert image to HEIC format."""
        try:
            if not HEIF_AVAILABLE:
                raise FileProcessingError("HEIC output support is not enabled. Please install 'pillow-heif' on the server.")
            
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ['RGBA', 'LA', 'P']:
                    img = img.convert('RGB')
                
                # Save as HEIC
                img.save(output_path, format='HEIF', quality=95)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"HEIC conversion failed: {str(e)}")
    
    @staticmethod
    def _convert_to_svg(input_path: str, output_path: str) -> str:
        """Convert image to SVG format."""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ['RGBA', 'LA', 'P']:
                    img = img.convert('RGB')
                
                # Create SVG content
                width, height = img.size
                svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <image href="data:image/png;base64,{base64.b64encode(io.BytesIO(img.tobytes()).getvalue()).decode()}" 
           width="{width}" height="{height}"/>
</svg>'''
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"SVG conversion failed: {str(e)}")
    
    @staticmethod
    def _convert_to_netpbm(input_path: str, output_path: str, format_type: str) -> str:
        """Convert image to PGM, PPM, or PAM format."""
        try:
            with Image.open(input_path) as img:
                # Convert to grayscale for PGM, RGB for PPM/PAM
                if format_type == 'PGM':
                    if img.mode != 'L':
                        img = img.convert('L')
                    img.save(output_path, format='PPM') # Pillow uses PPM for PGM too
                elif format_type == 'PPM':
                    if img.mode not in ['RGB', 'L']:
                        img = img.convert('RGB')
                    img.save(output_path, format='PPM')
                elif format_type == 'PAM':
                    # Pillow doesn't support PAM directly, implement manually
                    if img.mode not in ['RGB', 'RGBA', 'L']:
                        img = img.convert('RGB')
                    
                    width, height = img.size
                    mode = img.mode
                    
                    if mode == 'RGB':
                        depth = 3
                        tupltype = 'RGB'
                    elif mode == 'RGBA':
                        depth = 4
                        tupltype = 'RGB_ALPHA'
                    else: # L
                        depth = 1
                        tupltype = 'GRAYSCALE'
                    
                    header = f"P7\nWIDTH {width}\nHEIGHT {height}\nDEPTH {depth}\nMAXVAL 255\nTUPLTYPE {tupltype}\nENDHDR\n"
                    
                    with open(output_path, 'wb') as f:
                        f.write(header.encode('ascii'))
                        f.write(img.tobytes())
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"NetPBM conversion failed: {str(e)}")
    
    @staticmethod
    def _convert_to_yuv(input_path: str, output_path: str) -> str:
        """Convert image to YUV format (I420/YUV420P)."""
        try:
            # Try OpenCV first
            try:
                import cv2
                img = cv2.imread(input_path)
                if img is not None:
                    yuv_img = cv2.cvtColor(img, cv2.COLOR_BGR2YUV_I420)
                    with open(output_path, 'wb') as f:
                        f.write(yuv_img.tobytes())
                    return output_path
            except ImportError:
                pass

            # Fallback to PIL and numpy
            from PIL import Image
            import numpy as np
            
            with Image.open(input_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                width, height = img.size
                # Ensure width and height are even for YUV420P
                if width % 2 != 0 or height % 2 != 0:
                    img = img.resize((width // 2 * 2, height // 2 * 2))
                    width, height = img.size
                
                arr = np.array(img)
                
                # RGB to YUV coefficients (BT.601)
                r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
                
                y = 0.299 * r + 0.587 * g + 0.114 * b
                u = -0.169 * r - 0.331 * g + 0.500 * b + 128
                v = 0.500 * r - 0.419 * g - 0.081 * b + 128
                
                # Subsample U and V (YUV420P)
                u_sub = u[::2, ::2]
                v_sub = v[::2, ::2]
                
                # Combine into one byte array
                yuv_data = bytes(y.astype(np.uint8).tobytes()) + \
                           bytes(u_sub.astype(np.uint8).tobytes()) + \
                           bytes(v_sub.astype(np.uint8).tobytes())
                
                with open(output_path, 'wb') as f:
                    f.write(yuv_data)
                    
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"YUV conversion failed: {str(e)}")
    
    @staticmethod
    def get_supported_formats() -> Dict[str, List[str]]:
        """Get list of supported input and output formats."""
        return {
            "input_formats": list(ImageConversionService.SUPPORTED_INPUT_FORMATS),
            "output_formats": list(ImageConversionService.SUPPORTED_OUTPUT_FORMATS)
        }
    
    @staticmethod
    def cleanup_temp_files(*file_paths: str) -> None:
        """Clean up temporary files."""
        for file_path in file_paths:
            FileService.cleanup_file(file_path)

    @staticmethod
    def log_conversion(conversion_type: str, input_data: str, output_data: str, success: bool, error_message: str = None, user_id: int = None):
        """Log conversion operation to database."""
        try:
            RequestLoggingService.log_conversion_request(
                conversion_type=conversion_type,
                input_data=input_data,
                output_data=output_data,
                success=success,
                error_message=error_message,
                user_id=user_id
            )
        except Exception as e:
            logger.error(f"Error logging conversion: {str(e)}")

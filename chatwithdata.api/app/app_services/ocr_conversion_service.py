import os
import io
import base64
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from app.app_core.exceptions import FileProcessingError
from app.app_services.file_service import FileService
from app.app_core.ocr_utils import configure_tesseract, get_poppler_path


class OCRConversionService:
    """Service for handling OCR conversions and text extraction."""
    
    # Supported input formats for OCR
    SUPPORTED_INPUT_FORMATS = {
        'PNG', 'JPG', 'JPEG', 'TIFF', 'BMP', 'PDF'
    }
    
    @staticmethod
    def extract_text_from_image(input_path: str, language: str = 'eng', ocr_engine: str = 'tesseract') -> str:
        """Extract text from image using OCR."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input image file not found: {input_path}")
            
            # Load and preprocess image
            image = Image.open(input_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Preprocess image for better OCR
            processed_image = OCRConversionService._preprocess_image_for_ocr(image)
            
            # Extract text using specified OCR engine
            if ocr_engine.lower() == 'tesseract':
                text = OCRConversionService._extract_text_tesseract(processed_image, language)
            else:
                # Default to tesseract
                text = OCRConversionService._extract_text_tesseract(processed_image, language)
            
            return text.strip()
            
        except Exception as e:
            raise FileProcessingError(f"OCR text extraction failed: {str(e)}")
    
    @staticmethod
    def image_to_pdf_with_ocr(input_path: str, language: str = 'eng', ocr_engine: str = 'tesseract') -> str:
        """Convert image to PDF with OCR text layer."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input image file not found: {input_path}")
            
            # Extract text using OCR
            extracted_text = OCRConversionService.extract_text_from_image(input_path, language, ocr_engine)
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, "_ocr.pdf")
            
            # Create PDF with extracted text
            OCRConversionService._create_pdf_with_text(extracted_text, output_path, input_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"Image to PDF with OCR conversion failed: {str(e)}")
    
    @staticmethod
    def pdf_to_text_with_ocr(input_path: str, language: str = 'eng', ocr_engine: str = 'tesseract') -> str:
        """Extract text from PDF using OCR."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input PDF file not found: {input_path}")
            
            # First try to extract text directly from PDF
            try:
                doc = fitz.open(input_path)
                direct_text = ""
                for page in doc:
                    direct_text += page.get_text()
                doc.close()
                
                # If we got substantial text, return it
                if len(direct_text.strip()) > 50:
                    return direct_text.strip()
            except:
                pass  # Fall back to OCR
            
            # Convert PDF to images and extract text using OCR
            images = convert_from_path(input_path, dpi=300, poppler_path=get_poppler_path())
            all_text = ""
            
            for i, image in enumerate(images):
                # Save temporary image
                temp_path = FileService.get_output_path(f"temp_page_{i}", ".png")
                image.save(temp_path)
                
                try:
                    # Extract text from this page
                    page_text = OCRConversionService.extract_text_from_image(temp_path, language, ocr_engine)
                    all_text += f"\n--- Page {i+1} ---\n{page_text}\n"
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            
            return all_text.strip()
            
        except Exception as e:
            raise FileProcessingError(f"PDF to text with OCR conversion failed: {str(e)}")
    
    @staticmethod
    def pdf_image_to_pdf_text(input_path: str, language: str = 'eng', ocr_engine: str = 'tesseract') -> str:
        """Convert PDF with images to PDF with searchable text."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input PDF file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, "_searchable.pdf")
            
            # Open PDF
            # No changes needed here for fitz, but we might need poppler for other methods
            doc = fitz.open(input_path)
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # High resolution
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Save temporary image
                temp_path = FileService.get_output_path(f"temp_page_{page_num}", ".png")
                with open(temp_path, "wb") as f:
                    f.write(img_data)
                
                try:
                    # Extract text using OCR
                    extracted_text = OCRConversionService.extract_text_from_image(temp_path, language, ocr_engine)
                    
                    # Add text to PDF page
                    if extracted_text.strip():
                        # Create text block
                        text_rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
                        page.insert_textbox(text_rect, extracted_text, fontsize=12, color=(0, 0, 0))
                
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            
            # Save the modified PDF
            doc.save(output_path)
            doc.close()
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"PDF image to PDF text conversion failed: {str(e)}")
    
    @staticmethod
    def _preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply thresholding
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Convert back to PIL
            processed_image = Image.fromarray(thresh)
            
            return processed_image
            
        except Exception as e:
            # If preprocessing fails, return original image
            return image
    
    @staticmethod
    def _extract_text_tesseract(image: Image.Image, language: str = 'eng') -> str:
        """Extract text using Tesseract OCR."""
        try:
            # Configure tesseract path
            configure_tesseract()
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=language)
            return text
            
        except Exception as e:
            raise FileProcessingError(f"Tesseract OCR failed: {str(e)}")
    
    @staticmethod
    def _create_pdf_with_text(text: str, output_path: str, original_image_path: str):
        """Create PDF with extracted text and original image."""
        try:
            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            
            # Create styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=16,
                spaceAfter=20,
                alignment=1  # Center alignment
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                leading=14
            )
            
            # Build content
            content = []
            
            # Add title
            content.append(Paragraph("OCR Extracted Text", title_style))
            content.append(Spacer(1, 20))
            
            # Add extracted text
            if text.strip():
                # Split text into paragraphs
                paragraphs = text.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        content.append(Paragraph(para.strip(), normal_style))
                        content.append(Spacer(1, 6))
            else:
                content.append(Paragraph("No text could be extracted from the image.", normal_style))
            
            # Build PDF
            doc.build(content)
            
        except Exception as e:
            raise FileProcessingError(f"PDF creation failed: {str(e)}")
    
    @staticmethod
    def get_supported_languages() -> List[str]:
        """Get list of supported OCR languages."""
        try:
            # Get available languages from tesseract
            langs = pytesseract.get_languages()
            return langs
        except:
            # Return default languages if tesseract is not properly configured
            return ['eng', 'spa', 'fra', 'deu', 'ita', 'por', 'rus', 'ara', 'chi_sim', 'chi_tra']
    
    @staticmethod
    def get_supported_ocr_engines() -> List[str]:
        """Get list of supported OCR engines."""
        return ['tesseract']  # Can be extended with other engines
    
    @staticmethod
    def cleanup_temp_files(*file_paths: str) -> None:
        """Clean up temporary files."""
        for file_path in file_paths:
            FileService.cleanup_file(file_path)

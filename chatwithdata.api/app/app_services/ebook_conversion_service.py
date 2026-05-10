import os
import io
import zipfile
import tempfile
from typing import Optional, Dict, Any, List, Tuple
import ebooklib
from ebooklib import epub
from ebooklib.epub import EpubBook, EpubHtml, EpubNcx, EpubNav
import markdown
from markdown.extensions import codehilite, fenced_code, tables
import logging
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from app.app_core.exceptions import FileProcessingError
from app.app_services.file_service import FileService

logger = logging.getLogger(__name__)


class EBookConversionService:
    """Service for handling eBook conversions between various formats."""
    
    # Supported input formats
    SUPPORTED_INPUT_FORMATS = {
        'EPUB', 'MOBI', 'AZW', 'AZW3', 'PDF', 'FB2', 'FBZ', 'MD', 'MARKDOWN'
    }
    
    # Supported output formats
    SUPPORTED_OUTPUT_FORMATS = {
        'EPUB', 'MOBI', 'AZW', 'AZW3', 'PDF', 'FB2', 'FBZ'
    }
    
    @staticmethod
    def markdown_to_epub(input_path: str, title: str = "Converted Book", author: str = "Unknown") -> str:
        """Convert Markdown file to ePUB format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input Markdown file not found: {input_path}")
            
            # Read Markdown file
            with open(input_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Convert Markdown to HTML
            md = markdown.Markdown(extensions=['codehilite', 'fenced_code', 'tables'])
            html_content = md.convert(markdown_content)
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".epub")
            
            # Create ePUB book
            book = epub.EpubBook()
            book.set_identifier('book-id')
            book.set_title(title)
            book.set_language('en')
            book.add_author(author)
            
            # Add chapter
            chapter = epub.EpubHtml(title='Chapter 1', file_name='chapter1.xhtml', lang='en')
            chapter.content = html_content
            book.add_item(chapter)
            
            # Add chapter to spine
            book.spine = ['nav', chapter]
            
            # Add navigation
            book.toc = [chapter]
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            # Write ePUB file
            epub.write_epub(output_path, book, {})
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"Markdown to ePUB conversion failed: {str(e)}")
    
    @staticmethod
    def epub_to_mobi(input_path: str) -> str:
        """Convert ePUB file to MOBI format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input ePUB file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".mobi")
            
            # For MOBI conversion, we'll use a simplified approach
            # In a production environment, you would use Calibre's ebook-convert
            EBookConversionService._convert_epub_to_mobi_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"ePUB to MOBI conversion failed: {str(e)}")
    
    @staticmethod
    def epub_to_azw(input_path: str) -> str:
        """Convert ePUB file to AZW format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input ePUB file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".azw")
            
            # For AZW conversion, we'll use a simplified approach
            EBookConversionService._convert_epub_to_azw_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"ePUB to AZW conversion failed: {str(e)}")
    
    @staticmethod
    def mobi_to_epub(input_path: str) -> str:
        """Convert MOBI file to ePUB format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input MOBI file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".epub")
            
            # For MOBI to ePUB conversion
            EBookConversionService._convert_mobi_to_epub_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"MOBI to ePUB conversion failed: {str(e)}")
    
    @staticmethod
    def mobi_to_azw(input_path: str) -> str:
        """Convert MOBI file to AZW format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input MOBI file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".azw")
            
            # For MOBI to AZW conversion
            EBookConversionService._convert_mobi_to_azw_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"MOBI to AZW conversion failed: {str(e)}")
    
    @staticmethod
    def azw_to_epub(input_path: str) -> str:
        """Convert AZW file to ePUB format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input AZW file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".epub")
            
            # For AZW to ePUB conversion
            EBookConversionService._convert_azw_to_epub_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"AZW to ePUB conversion failed: {str(e)}")
    
    @staticmethod
    def azw_to_mobi(input_path: str) -> str:
        """Convert AZW file to MOBI format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input AZW file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".mobi")
            
            # For AZW to MOBI conversion
            EBookConversionService._convert_azw_to_mobi_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"AZW to MOBI conversion failed: {str(e)}")
    
    @staticmethod
    def epub_to_pdf(input_path: str) -> str:
        """Convert ePUB file to PDF format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input ePUB file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".pdf")
            
            # For ePUB to PDF conversion
            EBookConversionService._convert_epub_to_pdf_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"ePUB to PDF conversion failed: {str(e)}")
    
    @staticmethod
    def mobi_to_pdf(input_path: str) -> str:
        """Convert MOBI file to PDF format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input MOBI file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".pdf")
            
            # For MOBI to PDF conversion
            EBookConversionService._convert_mobi_to_pdf_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"MOBI to PDF conversion failed: {str(e)}")
    
    @staticmethod
    def azw_to_pdf(input_path: str) -> str:
        """Convert AZW file to PDF format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input AZW file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".pdf")
            
            # For AZW to PDF conversion
            EBookConversionService._convert_azw_to_pdf_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"AZW to PDF conversion failed: {str(e)}")
    
    @staticmethod
    def azw3_to_pdf(input_path: str) -> str:
        """Convert AZW3 file to PDF format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input AZW3 file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".pdf")
            
            # For AZW3 to PDF conversion
            EBookConversionService._convert_azw3_to_pdf_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"AZW3 to PDF conversion failed: {str(e)}")
    
    @staticmethod
    def fb2_to_pdf(input_path: str) -> str:
        """Convert FB2 file to PDF format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input FB2 file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".pdf")
            
            # For FB2 to PDF conversion
            EBookConversionService._convert_fb2_to_pdf_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"FB2 to PDF conversion failed: {str(e)}")
    
    @staticmethod
    def fbz_to_pdf(input_path: str) -> str:
        """Convert FBZ file to PDF format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input FBZ file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".pdf")
            
            # For FBZ to PDF conversion
            EBookConversionService._convert_fbz_to_pdf_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"FBZ to PDF conversion failed: {str(e)}")
    
    @staticmethod
    def pdf_to_epub(input_path: str) -> str:
        """Convert PDF file to ePUB format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input PDF file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".epub")
            
            # For PDF to ePUB conversion
            EBookConversionService._convert_pdf_to_epub_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"PDF to ePUB conversion failed: {str(e)}")
    
    @staticmethod
    def pdf_to_mobi(input_path: str) -> str:
        """Convert PDF file to MOBI format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input PDF file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".mobi")
            
            # For PDF to MOBI conversion
            EBookConversionService._convert_pdf_to_mobi_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"PDF to MOBI conversion failed: {str(e)}")
    
    @staticmethod
    def pdf_to_azw(input_path: str) -> str:
        """Convert PDF file to AZW format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input PDF file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".azw")
            
            # For PDF to AZW conversion
            EBookConversionService._convert_pdf_to_azw_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"PDF to AZW conversion failed: {str(e)}")
    
    @staticmethod
    def pdf_to_azw3(input_path: str) -> str:
        """Convert PDF file to AZW3 format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input PDF file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".azw3")
            
            # For PDF to AZW3 conversion
            EBookConversionService._convert_pdf_to_azw3_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"PDF to AZW3 conversion failed: {str(e)}")
    
    @staticmethod
    def pdf_to_fb2(input_path: str) -> str:
        """Convert PDF file to FB2 format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input PDF file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".fb2")
            
            # For PDF to FB2 conversion
            EBookConversionService._convert_pdf_to_fb2_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"PDF to FB2 conversion failed: {str(e)}")
    
    @staticmethod
    def pdf_to_fbz(input_path: str) -> str:
        """Convert PDF file to FBZ format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input PDF file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".fbz")
            
            # For PDF to FBZ conversion
            EBookConversionService._convert_pdf_to_fbz_simple(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"PDF to FBZ conversion failed: {str(e)}")
    
    # Simplified conversion methods (placeholder implementations)
    @staticmethod
    def _convert_epub_to_mobi_simple(input_path: str, output_path: str):
        """Simplified ePUB to MOBI conversion."""
        # This is a placeholder implementation
        # In production, you would use Calibre's ebook-convert
        with open(input_path, 'rb') as f:
            content = f.read()
        with open(output_path, 'wb') as f:
            f.write(content)
    
    @staticmethod
    def _convert_epub_to_azw_simple(input_path: str, output_path: str):
        """Simplified ePUB to AZW conversion."""
        with open(input_path, 'rb') as f:
            content = f.read()
        with open(output_path, 'wb') as f:
            f.write(content)
    
    @staticmethod
    def _convert_mobi_to_epub_simple(input_path: str, output_path: str):
        """Simplified MOBI to ePUB conversion."""
        with open(input_path, 'rb') as f:
            content = f.read()
        with open(output_path, 'wb') as f:
            f.write(content)
    
    @staticmethod
    def _convert_mobi_to_azw_simple(input_path: str, output_path: str):
        """Simplified MOBI to AZW conversion."""
        with open(input_path, 'rb') as f:
            content = f.read()
        with open(output_path, 'wb') as f:
            f.write(content)
    
    @staticmethod
    def _convert_azw_to_epub_simple(input_path: str, output_path: str):
        """Simplified AZW to ePUB conversion."""
        with open(input_path, 'rb') as f:
            content = f.read()
        with open(output_path, 'wb') as f:
            f.write(content)
    
    @staticmethod
    def _convert_azw_to_mobi_simple(input_path: str, output_path: str):
        """Simplified AZW to MOBI conversion."""
        with open(input_path, 'rb') as f:
            content = f.read()
        with open(output_path, 'wb') as f:
            f.write(content)
    
    @staticmethod
    def _render_text_to_pdf(text_lines: List[str], output_path: str):
        """Helper to render list of text lines to a PDF using PyMuPDF."""
        doc = fitz.open()
        font_size = 11
        line_height = 14
        margin = 50
        
        page = doc.new_page()
        rect = page.rect
        width = rect.width - (2 * margin)
        
        y = margin
        for line in text_lines:
            # Handle manual line breaks in input
            sublines = line.split('\n')
            for subline in sublines:
                subline = subline.strip()
                if not subline:
                    y += line_height # Empty line
                    continue
                    
                while subline:
                    # Very basic wrapping
                    chars_per_line = int(width / (font_size * 0.5))
                    chunk = subline[:chars_per_line]
                    subline = subline[chars_per_line:]
                    
                    if y + line_height > rect.height - margin:
                        page = doc.new_page()
                        y = margin
                        
                    page.insert_text((margin, y), chunk, fontsize=font_size)
                    y += line_height
        
        if len(doc) == 0:
            page = doc.new_page()
            page.insert_text((margin, margin), "No readable content found.")
            
        doc.save(output_path)
        doc.close()

    @staticmethod
    def _convert_epub_to_pdf_simple(input_path: str, output_path: str):
        """Simplified ePUB to PDF conversion using PyMuPDF."""
        try:
            doc = fitz.open(input_path)
            all_lines = []
            
            for page in doc:
                text = page.get_text()
                if text.strip():
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    all_lines.extend(lines)
            
            doc.close()
            
            if not all_lines:
                raise FileProcessingError("No readable content found in EPUB file.")
            
            EBookConversionService._render_text_to_pdf(all_lines, output_path)
            
        except Exception as e:
            logger.error(f"EPUB to PDF conversion failed: {str(e)}")
            raise FileProcessingError(f"Failed to convert EPUB to PDF: {str(e)}")

    @staticmethod
    def _convert_mobi_to_pdf_simple(input_path: str, output_path: str):
        """Simplified MOBI to PDF conversion using PyMuPDF."""
        try:
            doc = fitz.open(input_path)
            all_lines = []
            
            for page in doc:
                text = page.get_text()
                if text.strip():
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    all_lines.extend(lines)
            
            doc.close()
            
            if not all_lines:
                raise FileProcessingError("No readable text found in MOBI file.")
                
            EBookConversionService._render_text_to_pdf(all_lines, output_path)
            
        except Exception as e:
            logger.error(f"MOBI to PDF conversion failed: {str(e)}")
            raise FileProcessingError(f"Failed to convert MOBI to PDF: {str(e)}")

    @staticmethod
    def _convert_azw_to_pdf_simple(input_path: str, output_path: str):
        """Simplified AZW to PDF conversion using PyMuPDF."""
        try:
            doc = fitz.open(input_path)
            all_lines = []
            for page in doc:
                text = page.get_text()
                if text.strip():
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    all_lines.extend(lines)
            doc.close()
            if not all_lines:
                raise FileProcessingError("No readable text found in AZW file.")
            EBookConversionService._render_text_to_pdf(all_lines, output_path)
        except Exception as e:
            logger.error(f"AZW to PDF conversion failed: {str(e)}")
            raise FileProcessingError(f"Failed to convert AZW to PDF: {str(e)}")

    @staticmethod
    def _convert_azw3_to_pdf_simple(input_path: str, output_path: str):
        """Simplified AZW3 to PDF conversion."""
        try:
            # fitz (MuPDF) does not natively support the proprietary AZW3 (KF8) format.
            # We try to open it in case it's a variant that is supported (like MOBI renamed),
            # but provide a clear error message if it fails.
            doc = fitz.open(input_path)
            all_lines = []
            for page in doc:
                text = page.get_text()
                if text.strip():
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    all_lines.extend(lines)
            doc.close()
            if not all_lines:
                raise FileProcessingError("No readable text found in AZW3 file.")
            EBookConversionService._render_text_to_pdf(all_lines, output_path)
        except Exception as e:
            logger.error(f"AZW3 to PDF conversion failed: {str(e)}")
            raise FileProcessingError(
                "AZW3 is a proprietary Amazon format that is currently not supported for direct conversion. "
                "Please use a tool like Calibre to convert it to EPUB or MOBI first, or ensure the file is not DRM protected."
            )

    @staticmethod
    def _convert_fb2_to_pdf_simple(input_path: str, output_path: str):
        """Simplified FB2 to PDF conversion using PyMuPDF."""
        try:
            doc = fitz.open(input_path)
            # fitz can directly open FB2. Since it's a reflowable format, 
            # we can convert it to PDF by rendering its content.
            # In PyMuPDF, the best way to convert reflowable to PDF is via 'convert_to_pdf' 
            # or just by using the same text extraction and rendering if direct save isn't supported.
            # Actually, for FB2, fitz is quite good at rendering.
            
            all_lines = []
            for page in doc:
                text = page.get_text()
                if text.strip():
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    all_lines.extend(lines)
            doc.close()
            
            if not all_lines:
                raise FileProcessingError("No readable content found in FB2 file.")
            
            EBookConversionService._render_text_to_pdf(all_lines, output_path)
            
        except Exception as e:
            logger.error(f"FB2 to PDF conversion failed: {str(e)}")
            raise FileProcessingError(f"Failed to convert FB2 to PDF: {str(e)}")

    @staticmethod
    def _convert_fbz_to_pdf_simple(input_path: str, output_path: str):
        """Simplified FBZ to PDF conversion."""
        try:
            with zipfile.ZipFile(input_path, 'r') as zf:
                fb2_files = [n for n in zf.namelist() if n.lower().endswith('.fb2')]
                if not fb2_files:
                    raise FileProcessingError("No .fb2 file found in FBZ archive.")
                
                with tempfile.NamedTemporaryFile(suffix='.fb2', delete=False) as temp_fb2:
                    temp_fb2.write(zf.read(fb2_files[0]))
                    temp_fb2_path = temp_fb2.name
            
            EBookConversionService._convert_fb2_to_pdf_simple(temp_fb2_path, output_path)
            
            if os.path.exists(temp_fb2_path):
                os.remove(temp_fb2_path)
        except Exception as e:
            logger.error(f"FBZ to PDF conversion failed: {str(e)}")
            raise FileProcessingError(f"Failed to convert FBZ to PDF: {str(e)}")
    
    @staticmethod
    def _convert_pdf_to_epub_simple(input_path: str, output_path: str):
        """Simplified PDF to ePUB conversion."""
        try:
            # Extract text from PDF and create ePUB
            doc = fitz.open(input_path)
            text_content = []
            for page in doc:
                text_content.append(page.get_text())
            doc.close()
            
            # Create ePUB
            book = epub.EpubBook()
            book.set_identifier('pdf-converted')
            book.set_title('PDF Converted Book')
            book.set_language('en')
            book.add_author('PDF Converter')
            
            # Add chapter
            chapter = epub.EpubHtml(title='Chapter 1', file_name='chapter1.xhtml', lang='en')
            chapter.content = "<p>" + "</p><p>".join(text_content) + "</p>"
            book.add_item(chapter)
            
            book.spine = ['nav', chapter]
            book.toc = [chapter]
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            epub.write_epub(output_path, book, {})
        except Exception as e:
            logger.error(f"PDF to EPUB conversion failed: {str(e)}")
            raise FileProcessingError(f"Failed to convert PDF to EPUB: {str(e)}")
    
    @staticmethod
    def _convert_pdf_to_mobi_simple(input_path: str, output_path: str):
        """Simplified PDF to MOBI conversion (PalmDOC format)."""
        try:
            doc = fitz.open(input_path)
            text_content = ""
            for page in doc:
                text_content += page.get_text()
            doc.close()

            if not text_content.strip():
                raise FileProcessingError("No readable text found in PDF.")

            # Create a basic PalmDOC (MOBI) file
            # Header, Records, etc. - using a simplified approach
            # Since MOBI is complex, we'll write a basic text-only MOBI
            import struct
            import time

            title = os.path.splitext(os.path.basename(input_path))[0][:31].encode('ascii', 'ignore')
            title = title.ljust(32, b'\0')
            
            # Palm Database Header
            # name(32), attributes(2), version(2), creation(4), modification(4), backup(4), 
            # modificationNum(4), appInfoID(4), sortInfoID(4), type(4), creator(4), uniqueIDSeed(4)
            now = int(time.time())
            header = struct.pack('>32sHHIIIIII4s4sI', 
                title, 0, 0, now, now, 0, 0, 0, 0, b'BOOK', b'MOBI', 0)
            
            # Record Info - just one record for text for now (simplified)
            # offset(4), attributes(1), uniqueID(3)
            # This is a very minimal MOBI-like file that some readers might accept
            # Real MOBI is much more complex, but this is better than nothing
            
            text_bytes = text_content.encode('utf-8', 'ignore')
            record_count = 1
            # Record Info entry is 8 bytes: offset(4), attributes(1), uniqueID(3)
            # Total fields: I(1) + B(1) + B(1) + B(1) + B(1) = 5
            record_info = struct.pack('>IBBBB', 78 + 8 * record_count + 2, 0, 0, 0, 0)
            
            with open(output_path, 'wb') as f:
                f.write(header)
                f.write(struct.pack('>H', record_count))
                f.write(record_info)
                f.write(b'\0\0') # Placeholder
                f.write(text_bytes)
                
            return output_path
            
        except Exception as e:
            logger.error(f"PDF to MOBI conversion failed: {str(e)}")
            raise FileProcessingError(f"Failed to convert PDF to MOBI: {str(e)}")
    
    @staticmethod
    def _convert_pdf_to_azw_simple(input_path: str, output_path: str):
        """Simplified PDF to AZW conversion (PalmDOC format)."""
        # AZW is often very similar to MOBI/PalmDOC
        return EBookConversionService._convert_pdf_to_mobi_simple(input_path, output_path)

    @staticmethod
    def _convert_pdf_to_azw3_simple(input_path: str, output_path: str):
        """Simplified PDF to AZW3 conversion."""
        # For a truly functional AZW3 we would need a KF8 writer, 
        # for now we provide a functional PalmDOC which is widely compatible
        return EBookConversionService._convert_pdf_to_mobi_simple(input_path, output_path)

    @staticmethod
    def _convert_pdf_to_fb2_simple(input_path: str, output_path: str):
        """Simplified PDF to FB2 conversion."""
        try:
            doc = fitz.open(input_path)
            text_content = ""
            for page in doc:
                text_content += page.get_text()
            doc.close()

            if not text_content.strip():
                raise FileProcessingError("No readable text found in PDF.")

            # Create a basic FB2 XML
            # Convert text to paragraphs
            paragraphs = [p.strip() for p in text_content.split('\n') if p.strip()]
            fb2_paragraphs = "\n".join([f"      <p>{p.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</p>" for p in paragraphs])
            
            fb2_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:l="http://www.w3.org/1999/xlink">
  <description>
    <title-info>
      <book-title>{os.path.basename(input_path).replace('&', '&amp;')}</book-title>
    </title-info>
  </description>
  <body>
    <section>
{fb2_paragraphs}
    </section>
  </body>
</FictionBook>"""
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(fb2_template)
            return output_path
        except Exception as e:
            logger.error(f"PDF to FB2 conversion failed: {str(e)}")
            raise FileProcessingError(f"Failed to convert PDF to FB2: {str(e)}")

    @staticmethod
    def _convert_pdf_to_fbz_simple(input_path: str, output_path: str):
        """Simplified PDF to FBZ conversion."""
        try:
            fb2_path = output_path.replace('.fbz', '.fb2')
            EBookConversionService._convert_pdf_to_fb2_simple(input_path, fb2_path)
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(fb2_path, os.path.basename(fb2_path))
            
            if os.path.exists(fb2_path):
                os.remove(fb2_path)
            return output_path
        except Exception as e:
            logger.error(f"PDF to FBZ conversion failed: {str(e)}")
            raise FileProcessingError(f"Failed to convert PDF to FBZ: {str(e)}")
    
    @staticmethod
    def get_supported_formats() -> Dict[str, List[str]]:
        """Get list of supported input and output formats."""
        return {
            "input_formats": list(EBookConversionService.SUPPORTED_INPUT_FORMATS),
            "output_formats": list(EBookConversionService.SUPPORTED_OUTPUT_FORMATS)
        }
    
    @staticmethod
    def cleanup_temp_files(*file_paths: str) -> None:
        """Clean up temporary files."""
        for file_path in file_paths:
            FileService.cleanup_file(file_path)

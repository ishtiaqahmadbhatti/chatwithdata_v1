"""
CSV Conversion Service

This service handles various CSV conversion operations including HTML tables, Excel files,
OpenOffice Calc ODS files, PDFs, JSON, XML, BSON, and SRT files.
"""

import os
import json
import tempfile
import logging
import csv
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
from pathlib import Path
import base64
import io

# Document processing libraries
import pandas as pd
import docx
from pptx import Presentation
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from app.app_core.exceptions import FileProcessingError

# Database logging
from app.app_services.request_logging_service import RequestLoggingService
from app.app_services.xml_conversion_service import XMLConversionService

logger = logging.getLogger(__name__)


class CSVConversionService:
    """Service for CSV conversion operations."""
    
    @staticmethod
    def html_table_to_csv(html_content: str) -> str:
        """Convert HTML table to CSV."""
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find tables
            tables = soup.find_all('table')
            if not tables:
                raise Exception("No tables found in HTML content")
            
            csv_content = ""
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    csv_content += ','.join(f'"{cell}"' for cell in row_data) + '\n'
                csv_content += '\n'  # Separate tables
            
            return csv_content.strip()
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise FileProcessingError(f"Operation failed: {str(e)}")
    
    @staticmethod
    def excel_to_csv(file_content: bytes) -> str:
        """Convert Excel file to CSV."""
        try:
            # Create temporary file for Excel
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as excel_file:
                excel_file.write(file_content)
                excel_file_path = excel_file.name
            
            # Read Excel file
            df = pd.read_excel(excel_file_path, sheet_name=None)
            
            csv_content = ""
            
            for sheet_name, data in df.items():
                csv_content += f"# Sheet: {sheet_name}\n"
                csv_content += data.to_csv(index=False)
                csv_content += "\n\n"
            
            # Cleanup
            CSVConversionService.cleanup_temp_files([excel_file_path])
            
            return csv_content.strip()
            
        except Exception as e:
            logger.error(f"Error converting Excel to CSV: {str(e)}")
            raise FileProcessingError(f"Failed to convert Excel to CSV: {str(e)}")
    
    @staticmethod
    def ods_to_csv(file_content: bytes) -> str:
        """Convert OpenOffice Calc ODS file to CSV."""
        try:
            # Create temporary file for ODS
            with tempfile.NamedTemporaryFile(suffix='.ods', delete=False) as ods_file:
                ods_file.write(file_content)
                ods_file_path = ods_file.name
            
            # Read ODS file
            df = pd.read_excel(ods_file_path, sheet_name=None, engine='odf')
            
            csv_content = ""
            
            for sheet_name, data in df.items():
                csv_content += f"# Sheet: {sheet_name}\n"
                csv_content += data.to_csv(index=False)
                csv_content += "\n\n"
            
            # Cleanup
            CSVConversionService.cleanup_temp_files([ods_file_path])
            
            return csv_content.strip()
            
        except ImportError as e:
            logger.error(f"Missing dependency for ODS conversion: {str(e)}")
            raise FileProcessingError("Conversion failed: 'odfpy' library is required for ODS files. Please contact support.")
        except Exception as e:
            logger.error(f"Error converting ODS to CSV: {str(e)}")
            raise FileProcessingError(f"Failed to convert ODS to CSV: {str(e)}")
    
    @staticmethod
    def csv_to_excel(csv_content: str) -> str:
        """Convert CSV to Excel file."""
        try:
            import uuid
            
            # Create unique filename
            unique_id = str(uuid.uuid4())
            filename = f"csv_to_excel_{unique_id}.xlsx"
            output_path = os.path.join("outputs", filename)
            
            # Ensure outputs directory exists
            os.makedirs("outputs", exist_ok=True)
            
            # Read CSV content
            from io import StringIO
            df = pd.read_csv(StringIO(csv_content))
            
            # Save as Excel
            df.to_excel(output_path, index=False)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting CSV to Excel: {str(e)}")
            raise FileProcessingError(f"Failed to convert CSV to Excel: {str(e)}")
    
    @staticmethod
    def csv_to_xml(csv_content: str, root_name: str = "data") -> str:
        """Convert CSV to XML."""
        try:
            from io import StringIO
            
            # Read CSV content
            df = pd.read_csv(StringIO(csv_content))
            
            # Convert to XML
            xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n<{root_name}>\n'
            
            for index, row in df.iterrows():
                xml_content += f'  <record id="{index}">\n'
                for column, value in row.items():
                    # Clean column name for XML
                    clean_column = column.replace(' ', '_').replace('-', '_')
                    xml_content += f'    <{clean_column}>{value}</{clean_column}>\n'
                xml_content += '  </record>\n'
            
            xml_content += f'</{root_name}>'
            
            return xml_content
            
        except Exception as e:
            logger.error(f"Error converting CSV to XML: {str(e)}")
            raise FileProcessingError(f"Failed to convert CSV to XML: {str(e)}")
    
    @staticmethod
    def xml_to_csv(xml_content: str) -> str:
        """Convert XML to CSV."""
        try:
            return XMLConversionService.xml_to_csv(xml_content)
            
        except Exception as e:
            logger.error(f"Error converting XML to CSV: {str(e)}")
            raise FileProcessingError(f"Failed to convert XML to CSV: {str(e)}")
    
    @staticmethod
    def pdf_to_csv(file_content: bytes) -> str:
        """Convert PDF to CSV."""
        try:
            # Create temporary file for PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
                pdf_file.write(file_content)
                pdf_file_path = pdf_file.name
            
            # Read PDF
            doc = fitz.open(pdf_file_path)
            
            # Extract text and convert to CSV
            csv_content = "Page,Content\n"
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if text.strip():
                    # Clean text for CSV
                    clean_text = text.replace('"', '""').replace('\n', ' ')
                    csv_content += f"{page_num + 1},\"{clean_text}\"\n"
            
            # Cleanup
            CSVConversionService.cleanup_temp_files([pdf_file_path])
            
            return csv_content.strip()
            
        except Exception as e:
            logger.error(f"Error converting PDF to CSV: {str(e)}")
            raise FileProcessingError(f"Failed to convert PDF to CSV: {str(e)}")
    
    @staticmethod
    def json_to_csv(json_data: dict) -> str:
        """Convert JSON to CSV."""
        try:
            # Convert JSON to DataFrame
            if isinstance(json_data, list):
                df = pd.DataFrame(json_data)
            elif isinstance(json_data, dict):
                # Flatten nested dictionaries
                flattened = CSVConversionService._flatten_dict(json_data)
                df = pd.DataFrame([flattened])
            else:
                raise Exception("Invalid JSON format")
            
            # Convert to CSV
            return df.to_csv(index=False)
            
        except Exception as e:
            logger.error(f"Error converting JSON to CSV: {str(e)}")
            raise FileProcessingError(f"Failed to convert JSON to CSV: {str(e)}")
    
    @staticmethod
    def csv_to_json(csv_content: str) -> str:
        """Convert CSV to JSON."""
        try:
            from io import StringIO
            
            # Read CSV content
            df = pd.read_csv(StringIO(csv_content))
            
            # Convert to JSON
            json_data = df.to_dict('records')
            
            return json.dumps(json_data, indent=2)
            
        except Exception as e:
            logger.error(f"Error converting CSV to JSON: {str(e)}")
            raise FileProcessingError(f"Failed to convert CSV to JSON: {str(e)}")
    
    @staticmethod
    def json_objects_to_csv(json_objects: list) -> str:
        """Convert JSON objects to CSV."""
        try:
            # Convert JSON objects to DataFrame
            df = pd.DataFrame(json_objects)
            
            # Convert to CSV
            return df.to_csv(index=False)
            
        except Exception as e:
            logger.error(f"Error converting JSON objects to CSV: {str(e)}")
            raise FileProcessingError(f"Failed to convert JSON objects to CSV: {str(e)}")
    
    @staticmethod
    def bson_to_csv(bson_data: bytes) -> str:
        """Convert BSON to CSV."""
        try:
            import bson
            
            # Parse BSON
            bson_docs = bson.decode_all(bson_data)
            
            # Convert to DataFrame
            df = pd.DataFrame(bson_docs)
            
            # Convert to CSV
            return df.to_csv(index=False)
            
        except Exception as e:
            logger.error(f"Error converting BSON to CSV: {str(e)}")
            raise FileProcessingError(f"Failed to convert BSON to CSV: {str(e)}")
    
    @staticmethod
    def srt_to_csv(srt_content: str) -> str:
        """Convert SRT subtitle file to CSV."""
        try:
            # Parse SRT content
            srt_entries = CSVConversionService._parse_srt(srt_content)
            
            # Convert to CSV
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Index', 'Start_Time', 'End_Time', 'Text'])
            
            for entry in srt_entries:
                writer.writerow([
                    entry['index'],
                    entry['start_time'],
                    entry['end_time'],
                    entry['text']
                ])
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error converting SRT to CSV: {str(e)}")
            raise FileProcessingError(f"Failed to convert SRT to CSV: {str(e)}")
    
    @staticmethod
    def csv_to_srt(csv_content: str) -> str:
        """Convert CSV to SRT subtitle file."""
        try:
            from io import StringIO
            
            # Read CSV content
            df = pd.read_csv(StringIO(csv_content))
            
            # Generate SRT content
            srt_content = ""
            
            for index, row in df.iterrows():
                srt_content += f"{index + 1}\n"
                srt_content += f"{row.get('Start_Time', '00:00:00,000')} --> {row.get('End_Time', '00:00:00,000')}\n"
                srt_content += f"{row.get('Text', '')}\n\n"
            
            return srt_content.strip()
            
        except Exception as e:
            logger.error(f"Error converting CSV to SRT: {str(e)}")
            raise FileProcessingError(f"Failed to convert CSV to SRT: {str(e)}")
    
    @staticmethod
    def _flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(CSVConversionService._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    @staticmethod
    def _parse_srt(srt_content: str) -> list:
        """Parse SRT content into list of dictionaries."""
        entries = []
        blocks = srt_content.strip().split('\n\n')
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0])
                    time_line = lines[1]
                    text = '\n'.join(lines[2:])
                    
                    # Parse time
                    if ' --> ' in time_line:
                        start_time, end_time = time_line.split(' --> ')
                        entries.append({
                            'index': index,
                            'start_time': start_time.strip(),
                            'end_time': end_time.strip(),
                            'text': text
                        })
                except (ValueError, IndexError):
                    continue
        
        return entries
    
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
    
    @staticmethod
    def cleanup_temp_files(file_paths: list):
        """Clean up temporary files."""
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except Exception as e:
                    logger.warning(f"Could not delete temporary file {file_path}: {str(e)}")

"""
XML Conversion Service

This service handles various XML conversion operations including CSV, Excel, JSON conversions,
XML validation, and XML escaping fixes.
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
import re

# Document processing libraries
import pandas as pd
import docx
from pptx import Presentation
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from lxml import etree

# Database logging
from app.app_services.request_logging_service import RequestLoggingService

logger = logging.getLogger(__name__)


class XMLConversionService:
    """Service for XML conversion operations."""
    
    @staticmethod
    def csv_to_xml(csv_content: str, root_name: str = "data", record_name: str = "record") -> str:
        """Convert CSV to XML."""
        try:
            from io import StringIO
            
            # Read CSV content
            df = pd.read_csv(StringIO(csv_content))
            
            # Convert to XML
            xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n<{root_name}>\n'
            
            for index, row in df.iterrows():
                xml_content += f'  <{record_name} id="{index}">\n'
                for column, value in row.items():
                    # Clean column name for XML
                    clean_column = XMLConversionService._clean_tag_name(column)
                    # Escape XML special characters
                    escaped_value = XMLConversionService._escape_xml(str(value))
                    xml_content += f'    <{clean_column}>{escaped_value}</{clean_column}>\n'
                xml_content += f'  </{record_name}>\n'
            
            xml_content += f'</{root_name}>'
            
            return xml_content
            
        except Exception as e:
            logger.error(f"Error converting CSV to XML: {str(e)}")
            raise Exception(f"Failed to convert CSV to XML: {str(e)}")
    
    @staticmethod
    def excel_to_xml(file_content: bytes, root_name: str = "data", record_name: str = "record") -> str:
        """Convert Excel file to XML."""
        try:
            # Create temporary file for Excel
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as excel_file:
                excel_file.write(file_content)
                excel_file_path = excel_file.name
            
            # Read Excel file
            df = pd.read_excel(excel_file_path, sheet_name=None)
            
            xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n<{root_name}>\n'
            
            for sheet_name, data in df.items():
                xml_content += f'  <sheet name="{sheet_name}">\n'
                for index, row in data.iterrows():
                    xml_content += f'    <{record_name} id="{index}">\n'
                    for column, value in row.items():
                        clean_column = XMLConversionService._clean_tag_name(column)
                        escaped_value = XMLConversionService._escape_xml(str(value))
                        xml_content += f'      <{clean_column}>{escaped_value}</{clean_column}>\n'
                    xml_content += f'    </{record_name}>\n'
                xml_content += f'  </sheet>\n'
            
            xml_content += f'</{root_name}>'
            
            # Cleanup
            XMLConversionService.cleanup_temp_files([excel_file_path])
            
            return xml_content
            
        except Exception as e:
            logger.error(f"Error converting Excel to XML: {str(e)}")
            raise Exception(f"Failed to convert Excel to XML: {str(e)}")
    
    @staticmethod
    def xml_to_json(xml_content: str) -> str:
        """Convert XML to JSON."""
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Convert to dictionary
            def xml_to_dict(element):
                result = {}
                
                # Add attributes
                if element.attrib:
                    result['@attributes'] = element.attrib
                
                # Add text content
                if element.text and element.text.strip():
                    result['text'] = element.text.strip()
                
                # Add children
                children = {}
                for child in element:
                    child_dict = xml_to_dict(child)
                    if child.tag in children:
                        if not isinstance(children[child.tag], list):
                            children[child.tag] = [children[child.tag]]
                        children[child.tag].append(child_dict)
                    else:
                        children[child.tag] = child_dict
                
                if children:
                    result.update(children)
                
                return result
            
            # Convert to JSON
            json_data = xml_to_dict(root)
            return json.dumps(json_data, indent=2)
            
        except Exception as e:
            logger.error(f"Error converting XML to JSON: {str(e)}")
            raise Exception(f"Failed to convert XML to JSON: {str(e)}")
    
    @staticmethod
    def xml_to_csv(xml_content: str) -> str:
        """Convert XML to CSV."""
        try:
            records = XMLConversionService._extract_records_from_xml(xml_content)
            
            if not records:
                raise Exception("No records found in XML")
            
            # Convert to CSV
            import io
            output = io.StringIO()
            
            # Get all unique keys
            all_keys = set()
            for record in records:
                all_keys.update(record.keys())
            
            # Write CSV
            writer = csv.DictWriter(output, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(records)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error converting XML to CSV: {str(e)}")
            raise Exception(f"Failed to convert XML to CSV: {str(e)}")
    
    @staticmethod
    def xml_to_excel(xml_content: str) -> str:
        """Convert XML to Excel file."""
        try:
            import uuid
            
            # Create unique filename
            unique_id = str(uuid.uuid4())
            filename = f"xml_to_excel_{unique_id}.xlsx"
            output_path = os.path.join("outputs", filename)
            
            # Ensure outputs directory exists
            os.makedirs("outputs", exist_ok=True)
            
            records = XMLConversionService._extract_records_from_xml(xml_content)
            
            if not records:
                raise Exception("No records found in XML")
            
            # Convert to DataFrame and save as Excel
            df = pd.DataFrame(records)
            df.to_excel(output_path, index=False)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting XML to Excel: {str(e)}")
            raise Exception(f"Failed to convert XML to Excel: {str(e)}")

    @staticmethod
    def _extract_records_from_xml(xml_content: str) -> List[Dict[str, Any]]:
        """Extract flat records from XML content."""
        root = ET.fromstring(xml_content)
        records = []
        
        # Priority 1: explicitly named 'record' tags (as per original logic)
        elements = root.findall('.//record')
        
        # Priority 2: direct children of root (generic XML behavior)
        if not elements:
            elements = list(root)
            
        for element in elements:
            # Flatten the element into a dictionary
            record = XMLConversionService._flatten_xml_element(element)
            
            # If flattening didn't yield anything (empty tags), check attributes or text
            if not record:
                 # Check for attributes
                 if element.attrib:
                     record.update(element.attrib)
                 
                 # Check for direct text
                 if element.text and element.text.strip():
                     # Assuming formatting like <item>Value</item> -> {'item': 'Value'} is desired for the row
                     # But here 'element' IS the row. So column name?
                     # Ideally mixed content isn't great for CSV. 
                     # If the row element itself has value, what column name? 'value'? 'text'?
                     # Or use the tag name if we are treating children as rows.
                     pass 

            if record:
                records.append(record)
                
        return records

    @staticmethod
    def _flatten_xml_element(element, parent_key='', sep='_') -> Dict[str, str]:
        """Recursive helper to flatten XML element."""
        items = {}
        for child in element:
            new_key = f"{parent_key}{sep}{child.tag}" if parent_key else child.tag
            
            # If child has children, recurse
            if len(list(child)) > 0:
                items.update(XMLConversionService._flatten_xml_element(child, new_key, sep=sep))
            else:
                # Leaf node: get text
                items[new_key] = child.text or ''
                
        return items
    
    @staticmethod
    def fix_xml_escaping(xml_content: str) -> str:
        """Fix XML escaping issues."""
        try:
            # Common XML escaping issues and fixes
            fixes = {
                '&amp;amp;': '&amp;',  # Double encoded ampersand
                '&amp;lt;': '&lt;',    # Double encoded less than
                '&amp;gt;': '&gt;',    # Double encoded greater than
                '&amp;quot;': '&quot;', # Double encoded quote
                '&amp;#39;': '&#39;',  # Double encoded apostrophe
                '&amp;apos;': '&apos;', # Double encoded apostrophe
            }
            
            # Apply fixes
            fixed_xml = xml_content
            for wrong, correct in fixes.items():
                fixed_xml = fixed_xml.replace(wrong, correct)
            
            # Additional cleanup for common issues
            fixed_xml = re.sub(r'&amp;([^;]+);', r'&\1;', fixed_xml)  # Fix double encoded entities
            
            # Validate the fixed XML
            try:
                ET.fromstring(fixed_xml)
                return fixed_xml
            except ET.ParseError:
                # If still invalid, try to parse and reconstruct
                try:
                    # Remove invalid characters
                    fixed_xml = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\x85\xA0-\xFF]', '', fixed_xml)
                    ET.fromstring(fixed_xml)
                    return fixed_xml
                except ET.ParseError as e:
                    raise Exception(f"Unable to fix XML escaping: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error fixing XML escaping: {str(e)}")
            raise Exception(f"Failed to fix XML escaping: {str(e)}")
    

    
    @staticmethod
    def xml_xsd_validator(xml_content: str, xsd_content: str = None) -> dict:
        """Validate XML against XSD schema."""
        try:
            # Parse XML
            xml_doc = etree.fromstring(xml_content.encode('utf-8'))
            
            if xsd_content:
                # Parse XSD schema
                xsd_doc = etree.fromstring(xsd_content.encode('utf-8'))
                schema = etree.XMLSchema(xsd_doc)
                
                # Validate XML against XSD
                is_valid = schema.validate(xml_doc)
                errors = []
                
                if not is_valid:
                    for error in schema.error_log:
                        errors.append({
                            'line': error.line,
                            'column': error.column,
                            'message': error.message,
                            'level': error.level_name
                        })
                
                return {
                    'valid': is_valid,
                    'errors': errors,
                    'schema_used': True
                }
            else:
                # Basic XML validation
                try:
                    etree.tostring(xml_doc, encoding='unicode')
                    return {
                        'valid': True,
                        'errors': [],
                        'schema_used': False
                    }
                except Exception as e:
                    return {
                        'valid': False,
                        'errors': [{'message': str(e)}],
                        'schema_used': False
                    }
            
        except etree.XMLSyntaxError as e:
            return {
                'valid': False,
                'errors': [{
                    'line': e.position[0] if hasattr(e, 'position') else None,
                    'column': e.position[1] if hasattr(e, 'position') else None,
                    'message': str(e),
                    'level': 'error'
                }],
                'schema_used': xsd_content is not None
            }
        except Exception as e:
            logger.error(f"Error validating XML: {str(e)}")
            raise Exception(f"Failed to validate XML: {str(e)}")
    
    @staticmethod
    def json_to_xml(json_data: dict, root_name: str = "root") -> str:
        """Convert JSON to XML."""
        try:
            def dict_to_xml(data, root_name):
                if isinstance(data, dict):
                    xml = f'<{root_name}>\n'
                    for key, value in data.items():
                        if isinstance(value, dict):
                            xml += dict_to_xml(value, key)
                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    xml += dict_to_xml(item, key)
                                else:
                                    xml += f'<{key}>{XMLConversionService._escape_xml(str(item))}</{key}>\n'
                        else:
                            xml += f'<{key}>{XMLConversionService._escape_xml(str(value))}</{key}>\n'
                    xml += f'</{root_name}>\n'
                    return xml
                else:
                    return f'<{root_name}>{XMLConversionService._escape_xml(str(data))}</{root_name}>\n'
            
            xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n{dict_to_xml(json_data, root_name)}'
            return xml_content
            
        except Exception as e:
            logger.error(f"Error converting JSON to XML: {str(e)}")
            raise Exception(f"Failed to convert JSON to XML: {str(e)}")
    
    @staticmethod
    def _clean_tag_name(name: str) -> str:
        """Clean string to be a valid XML tag name."""
        name = str(name).strip()
        # Replace spaces, dashes, colons (namespace separator), parens with underscore
        name = re.sub(r'[\s\-:().]+', '_', name)
        # Remove any other invalid characters (keep alphanum and _)
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        
        # XML tags cannot start with a number
        if name and name[0].isdigit():
            name = f'_{name}'
            
        # Ensure it's not empty
        if not name:
            name = 'field'
            
        return name

    @staticmethod
    def _escape_xml(text: str) -> str:
        """Escape XML special characters."""
        if not text:
            return ""
        
        # Replace XML special characters
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&apos;')
        
        return text
    
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

import json
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser
import csv
import yaml
import pandas as pd
import io
import os
import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from app.app_core.exceptions import FileProcessingError
from app.app_services.file_service import FileService
from app.app_services.request_logging_service import RequestLoggingService


class JSONConversionService:
    """Service for handling JSON conversion operations."""
    
    @staticmethod
    def xml_to_json(xml_content: str) -> Dict[str, Any]:
        """Convert XML string to JSON."""
        try:
            # Clean and prepare XML content
            xml_data = xml_content.strip()
            
            # Remove BOM if present
            if xml_data.startswith('\ufeff'):
                xml_data = xml_data[1:]
            
            # Ensure XML is not empty
            if not xml_data:
                raise FileProcessingError("XML content is empty")
            
            # Try to fix common XML issues
            # Remove null bytes
            xml_data = xml_data.replace('\x00', '')
            
            # Validate XML structure
            if not xml_data.strip().startswith('<'):
                raise FileProcessingError(
                    "Invalid XML: XML must start with '<' or '<?xml' declaration. "
                    "Please check your XML format."
                )
            
            # Extract comments before parsing (ElementTree doesn't preserve them by default)
            # Store comments with their positions for better reconstruction
            comments = []
            comment_pattern = r'<!--(.*?)-->'
            comment_matches = list(re.finditer(comment_pattern, xml_data, re.DOTALL))
            for match in comment_matches:
                comment_text = match.group(1)  # Don't strip - preserve original
                if comment_text:
                    comments.append({
                        'position': match.start(),
                        'text': comment_text,
                        'original': match.group(0)  # Preserve original comment format
                    })
            
            # Store comments in a structured way for JSON output
            comments_dict = {}
            if comments:
                comments_dict['_comments'] = [c['text'] for c in comments]
            
            # Preserve CDATA sections
            cdata_pattern = r'<!\[CDATA\[(.*?)\]\]>'
            cdata_matches = list(re.finditer(cdata_pattern, xml_data, re.DOTALL))
            cdata_map = {}
            for idx, match in enumerate(cdata_matches):
                cdata_content = match.group(1)
                placeholder = f'__CDATA_PLACEHOLDER_{idx}__'
                cdata_map[placeholder] = cdata_content
                xml_data = xml_data.replace(match.group(0), placeholder)
            
            # Parse XML with error recovery
            try:
                root = ET.fromstring(xml_data)
            except ET.ParseError as parse_err:
                # Provide more helpful error message
                error_msg = str(parse_err)
                if "not well-formed" in error_msg.lower():
                    raise FileProcessingError(
                        f"XML is not well-formed: {error_msg}. "
                        "Please check: 1) All tags are properly closed, 2) No invalid characters, "
                        "3) Proper XML structure (e.g., <tag>content</tag>)"
                    )
                elif "unexpected token" in error_msg.lower() or "unclosed" in error_msg.lower():
                    raise FileProcessingError(
                        f"XML parsing error: {error_msg}. "
                        "Check for unclosed tags, missing closing brackets, or invalid characters."
                    )
                else:
                    raise FileProcessingError(f"XML parsing failed: {error_msg}. Please validate your XML format.")
            
            # Capture namespace declarations for cleaner attribute names
            namespace_uri_to_prefix = {}
            namespace_prefix_to_uri = {}
            namespace_pattern = r'xmlns(?::(\w+))?="([^"]+)"'
            for match in re.findall(namespace_pattern, xml_content):
                prefix = match[0] or ""
                uri = match[1]
                namespace_uri_to_prefix[uri] = prefix
                namespace_prefix_to_uri[prefix] = uri
            
            def format_name(name: str) -> str:
                """Format XML tag/attribute name with namespace prefixes."""
                if name.startswith('{'):
                    uri, local = name[1:].split('}', 1)
                    prefix = namespace_uri_to_prefix.get(uri)
                    return f"{prefix}:{local}" if prefix else local
                return name
            
            # Convert to dictionary with cleaned structure
            def xml_to_dict(element):
                node: Dict[str, Any] = {}
                
                # Attributes
                if element.attrib:
                    attrs = {}
                    for key, value in element.attrib.items():
                        attrs[format_name(key)] = value
                    if attrs:
                        node['@attributes'] = attrs
                
                # Text content (trim whitespace-only nodes)
                text_content = element.text or ""
                text_stripped = text_content.strip()
                if text_stripped:
                    text_to_store = text_stripped
                    for placeholder, cdata_content in cdata_map.items():
                        if placeholder in text_to_store:
                            text_to_store = text_to_store.replace(
                                placeholder,
                                f"<![CDATA[{cdata_content}]]>"
                            )
                    if len(element) == 0 and not element.attrib:
                        return text_to_store
                    node['#text'] = text_to_store
                
                # Children
                children: Dict[str, List[Any]] = {}
                for child in element:
                    child_name = format_name(child.tag)
                    child_value = xml_to_dict(child)
                    children.setdefault(child_name, []).append(child_value)
                
                for key, values in children.items():
                    if len(values) == 1:
                        node[key] = values[0]
                    else:
                        node[key] = values
                
                return node
            
            root_dict = xml_to_dict(root)
            root_name = format_name(root.tag)
                
            # Inject namespace declarations into root attributes
            if namespace_prefix_to_uri:
                ns_attrs = {}
                for prefix, uri in namespace_prefix_to_uri.items():
                    attr_name = f"xmlns:{prefix}" if prefix else "xmlns"
                    ns_attrs[attr_name] = uri
                if isinstance(root_dict, dict):
                    root_attrs = root_dict.setdefault('@attributes', {})
                    for key, value in ns_attrs.items():
                        root_attrs.setdefault(key, value)
                    else:
                        root_dict = {
                            '@attributes': ns_attrs,
                            '#text': root_dict
                        }
            
            # Attach comments at root level (trimmed)
            if comments:
                cleaned_comments = [c['text'].strip() for c in comments if c['text'].strip()]
                if cleaned_comments:
                    if isinstance(root_dict, dict):
                        root_dict['_comments'] = cleaned_comments
                    else:
                        root_dict = {
                            root_name: root_dict,
                            '_comments': cleaned_comments
                        }
            
            return {root_name: root_dict}
            
        except FileProcessingError:
            # Re-raise FileProcessingError as-is
            raise
        except ET.ParseError as e:
            raise FileProcessingError(f"Invalid XML format: {str(e)}. Please check your XML syntax.")
        except Exception as e:
            raise FileProcessingError(f"XML to JSON conversion failed: {str(e)}")
    
    @staticmethod
    def json_to_xml(json_data: Dict[str, Any], root_name: str = "root") -> str:
        """Convert JSON to XML string."""
        try:
            def dict_to_xml(data, root):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key == '@attributes':
                            root.attrib.update(value)
                        elif key == '#text':
                            root.text = str(value)
                        else:
                            if isinstance(value, list):
                                for item in value:
                                    child = ET.SubElement(root, key)
                                    dict_to_xml(item, child)
                            else:
                                child = ET.SubElement(root, key)
                                dict_to_xml(value, child)
                else:
                    root.text = str(data)
            
            root = ET.Element(root_name)
            dict_to_xml(json_data, root)
            
            # Convert to string
            return ET.tostring(root, encoding='unicode')
            
        except Exception as e:
            raise FileProcessingError(f"JSON to XML conversion failed: {str(e)}")
    
    @staticmethod
    def format_json(json_data: Union[str, Dict, List]) -> str:
        """Format JSON with proper indentation."""
        try:
            if isinstance(json_data, str):
                parsed = json.loads(json_data)
            else:
                parsed = json_data
            
            return json.dumps(parsed, indent=2, ensure_ascii=False)
            
        except json.JSONDecodeError as e:
            raise FileProcessingError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise FileProcessingError(f"JSON formatting failed: {str(e)}")
    
    @staticmethod
    def validate_json(json_data: str) -> Dict[str, Any]:
        """Validate JSON and return validation result."""
        try:
            parsed = json.loads(json_data)
            return {
                "valid": True,
                "message": "JSON is valid",
                "size": len(json_data),
                "structure": JSONConversionService._analyze_structure(parsed)
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "message": f"Invalid JSON: {str(e)}",
                "error_line": getattr(e, 'lineno', None),
                "error_column": getattr(e, 'colno', None)
            }
        except Exception as e:
            return {
                "valid": False,
                "message": f"Validation error: {str(e)}"
            }
    
    @staticmethod
    def json_to_csv(json_data: Union[Dict, List], delimiter: str = ",") -> str:
        """Convert JSON to CSV format."""
        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            
            # Handle single object by wrapping in list
            if isinstance(data, dict):
                data = [data]
            
            if isinstance(data, list):
                if not data:
                    return ""
                
                # Get all unique keys
                all_keys = set()
                for item in data:
                    if isinstance(item, dict):
                        all_keys.update(item.keys())
                
                if not all_keys:
                    return ""

                # Create CSV
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=sorted(all_keys), delimiter=delimiter)
                writer.writeheader()
                
                for item in data:
                    if isinstance(item, dict):
                        # Handle values that might be None or non-string
                        row = {}
                        for k, v in item.items():
                            if v is None:
                                row[k] = ""
                            elif isinstance(v, (dict, list)):
                                row[k] = json.dumps(v)
                            else:
                                row[k] = v
                        writer.writerow(row)
                
                return output.getvalue()
            else:
                raise FileProcessingError("JSON must be an array of objects or a single object for CSV conversion")
                
        except Exception as e:
            raise FileProcessingError(f"JSON to CSV conversion failed: {str(e)}")
    
    @staticmethod
    def json_to_excel(json_data: Union[Dict, List], filename: str = None) -> str:
        """Convert JSON to Excel file."""
        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            
            if filename is None:
                filename = f"converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            output_path = FileService.get_output_path(filename, ".xlsx")
            
            if isinstance(data, list):
                # Preprocess list data to handle nested objects and nulls
                processed_data = []
                for item in data:
                    if isinstance(item, dict):
                        row = {}
                        for k, v in item.items():
                            if v is None:
                                row[k] = ""
                            elif isinstance(v, (dict, list)):
                                row[k] = json.dumps(v)
                            else:
                                row[k] = v
                        processed_data.append(row)
                    else:
                         # Handle primitive types in list by wrapping them
                        processed_data.append({"value": item})
                df = pd.DataFrame(processed_data)
            elif isinstance(data, dict):
                 # Check if it is a columnar format (all values are lists of same length)
                is_columnar = all(isinstance(v, (list, tuple)) for v in data.values())
                
                if is_columnar:
                    df = pd.DataFrame(data)
                else:
                    # Single record
                    # Preprocess single record
                    row = {}
                    for k, v in data.items():
                        if v is None:
                            row[k] = ""
                        elif isinstance(v, (dict, list)):
                            row[k] = json.dumps(v)
                        else:
                            row[k] = v
                    df = pd.DataFrame([row])
            else:
                raise FileProcessingError("Unsupported JSON structure for Excel conversion")
            
            df.to_excel(output_path, index=False)
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"JSON to Excel conversion failed: {str(e)}")
    
    @staticmethod
    def excel_to_json(file_path: str) -> Dict[str, Any]:
        """Convert Excel file to JSON."""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Convert to JSON
            result = {
                "data": df.to_dict('records'),
                "columns": df.columns.tolist(),
                "shape": df.shape,
                "info": {
                    "rows": len(df),
                    "columns": len(df.columns)
                }
            }
            
            return result
            
        except Exception as e:
            raise FileProcessingError(f"Excel to JSON conversion failed: {str(e)}")
    
    @staticmethod
    def csv_to_json(csv_content: str, delimiter: str = ",") -> List[Dict[str, Any]]:
        """Convert CSV string to JSON."""
        try:
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(csv_content), delimiter=delimiter)
            data = list(csv_reader)
            
            return data
            
        except Exception as e:
            raise FileProcessingError(f"CSV to JSON conversion failed: {str(e)}")
    
    @staticmethod
    def json_to_yaml(json_data: Union[Dict, List]) -> str:
        """Convert JSON to YAML."""
        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            
            return yaml.dump(data, default_flow_style=False, allow_unicode=True)
            
        except Exception as e:
            raise FileProcessingError(f"JSON to YAML conversion failed: {str(e)}")
    
    @staticmethod
    def yaml_to_json(yaml_content: str) -> Dict[str, Any]:
        """Convert YAML to JSON."""
        try:
            data = yaml.safe_load(yaml_content)
            return data
            
        except yaml.YAMLError as e:
            raise FileProcessingError(f"Invalid YAML format: {str(e)}")
        except Exception as e:
            raise FileProcessingError(f"YAML to JSON conversion failed: {str(e)}")
    
    @staticmethod
    def json_objects_to_csv(json_data: List[Dict], delimiter: str = ",") -> str:
        """Convert JSON objects array to CSV."""
        try:
            if not isinstance(json_data, list):
                raise FileProcessingError("Input must be a list of JSON objects")
            
            if not json_data:
                return ""
            
            # Get all unique keys
            all_keys = set()
            for item in json_data:
                if isinstance(item, dict):
                    all_keys.update(item.keys())
            
            # Create CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=sorted(all_keys), delimiter=delimiter)
            writer.writeheader()
            
            for item in json_data:
                if isinstance(item, dict):
                    writer.writerow(item)
            
            return output.getvalue()
            
        except Exception as e:
            raise FileProcessingError(f"JSON objects to CSV conversion failed: {str(e)}")
    
    @staticmethod
    def json_objects_to_excel(json_data: List[Dict], filename: str = None) -> str:
        """Convert JSON objects array to Excel."""
        try:
            if not isinstance(json_data, list):
                raise FileProcessingError("Input must be a list of JSON objects")
            
            if filename is None:
                filename = f"converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            output_path = FileService.get_output_path(filename, ".xlsx")
            
            df = pd.DataFrame(json_data)
            df.to_excel(output_path, index=False)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"JSON objects to Excel conversion failed: {str(e)}")
    
    @staticmethod
    def _analyze_structure(data: Any) -> Dict[str, Any]:
        """Analyze JSON structure."""
        if isinstance(data, dict):
            return {
                "type": "object",
                "keys": list(data.keys()),
                "size": len(data)
            }
        elif isinstance(data, list):
            return {
                "type": "array",
                "length": len(data),
                "item_types": list(set(type(item).__name__ for item in data)) if data else []
            }
        else:
            return {
                "type": type(data).__name__,
                "value": str(data)[:100] if len(str(data)) > 100 else str(data)
            }
    
    @staticmethod
    def log_conversion(conversion_type: str, input_data: str, output_data: str, 
                      success: bool, error_message: str = None, user_id: str = None):
        """Log conversion operation to database."""
        try:
            RequestLoggingService.log_request(
                endpoint=f"/api/v1/convert/json/{conversion_type}",
                method="POST",
                user_id=user_id,
                request_data={"conversion_type": conversion_type},
                response_data={
                    "success": success,
                    "input_size": len(input_data) if input_data else 0,
                    "output_size": len(output_data) if output_data else 0,
                    "error_message": error_message
                },
                status_code=200 if success else 400
            )
        except Exception as e:
            print(f"Warning: Failed to log conversion: {str(e)}")
    
    @staticmethod
    def cleanup_temp_files(*file_paths: str) -> None:
        """Clean up temporary files."""
        for file_path in file_paths:
            FileService.cleanup_file(file_path)

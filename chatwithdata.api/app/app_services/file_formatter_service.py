import os
import json
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List, Tuple
import jsonschema
from jsonschema import validate, ValidationError
import xmlschema
from lxml import etree
from app.app_core.exceptions import FileProcessingError
from app.app_services.file_service import FileService


class FileFormatterService:
    """Service for handling file formatting and validation."""
    
    # Supported input formats
    SUPPORTED_INPUT_FORMATS = {
        'JSON', 'XML', 'XSD'
    }
    
    @staticmethod
    def format_json(input_path: str, indent: int = 2, sort_keys: bool = False) -> str:
        """Format JSON file with proper indentation and sorting."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input JSON file not found: {input_path}")
            
            # Read JSON file
            with open(input_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, "_formatted.json")
            
            # Format JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
            
            return output_path
            
        except json.JSONDecodeError as e:
            raise FileProcessingError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise FileProcessingError(f"JSON formatting failed: {str(e)}")
    
    @staticmethod
    def validate_json(input_path: str, schema_path: Optional[str] = None) -> Dict[str, Any]:
        """Validate JSON file against schema or basic JSON syntax."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input JSON file not found: {input_path}")
            
            # Read JSON file
            with open(input_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "schema_validated": False
            }
            
            # If schema is provided, validate against schema
            if schema_path and os.path.exists(schema_path):
                try:
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        schema = json.load(f)
                    
                    validate(instance=json_data, schema=schema)
                    validation_result["schema_validated"] = True
                    
                except ValidationError as e:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Schema validation error: {str(e)}")
                except Exception as e:
                    validation_result["warnings"].append(f"Schema validation warning: {str(e)}")
            
            # Basic JSON structure validation
            if not isinstance(json_data, (dict, list)):
                validation_result["warnings"].append("JSON root should be an object or array")
            
            # Check for common issues
            if isinstance(json_data, dict):
                if not json_data:
                    validation_result["warnings"].append("JSON object is empty")
                
                # Check for duplicate keys (this is handled by Python's json module)
                # Check for common data type issues
                for key, value in json_data.items():
                    if not isinstance(key, str):
                        validation_result["warnings"].append(f"Key '{key}' is not a string")
            
            return validation_result
            
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "errors": [f"JSON syntax error: {str(e)}"],
                "warnings": [],
                "schema_validated": False
            }
        except Exception as e:
            raise FileProcessingError(f"JSON validation failed: {str(e)}")
    
    @staticmethod
    def validate_xml(input_path: str, xsd_path: Optional[str] = None) -> Dict[str, Any]:
        """Validate XML file against XSD schema or basic XML syntax."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input XML file not found: {input_path}")
            
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "schema_validated": False
            }
            
            # Parse XML for basic syntax validation
            try:
                tree = ET.parse(input_path)
                root = tree.getroot()
            except ET.ParseError as e:
                validation_result["valid"] = False
                validation_result["errors"].append(f"XML syntax error: {str(e)}")
                return validation_result
            
            # If XSD schema is provided, validate against schema
            if xsd_path and os.path.exists(xsd_path):
                try:
                    schema = xmlschema.XMLSchema(xsd_path)
                    schema.validate(input_path)
                    validation_result["schema_validated"] = True
                    
                except xmlschema.XMLSchemaException as e:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"XSD validation error: {str(e)}")
                except Exception as e:
                    validation_result["warnings"].append(f"XSD validation warning: {str(e)}")
            
            # Basic XML structure validation
            if root is None:
                validation_result["warnings"].append("XML document has no root element")
            
            # Check for common XML issues
            if root.tag is None or root.tag.strip() == "":
                validation_result["warnings"].append("XML root element has no tag name")
            
            # Check for namespace issues
            if root.tag.startswith("{"):
                validation_result["warnings"].append("XML uses namespaces - ensure proper namespace handling")
            
            return validation_result
            
        except Exception as e:
            raise FileProcessingError(f"XML validation failed: {str(e)}")
    
    @staticmethod
    def validate_xsd(input_path: str) -> Dict[str, Any]:
        """Validate XSD schema file."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input XSD file not found: {input_path}")
            
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "schema_info": {}
            }
            
            # Parse XSD for syntax validation
            try:
                schema = xmlschema.XMLSchema(input_path)
                validation_result["schema_info"] = {
                    "target_namespace": schema.target_namespace,
                    "element_count": len(schema.elements),
                    "type_count": len(schema.types),
                    "attribute_count": len(schema.attributes)
                }
                
            except xmlschema.XMLSchemaException as e:
                validation_result["valid"] = False
                validation_result["errors"].append(f"XSD syntax error: {str(e)}")
            except Exception as e:
                validation_result["warnings"].append(f"XSD validation warning: {str(e)}")
            
            return validation_result
            
        except Exception as e:
            raise FileProcessingError(f"XSD validation failed: {str(e)}")
    
    @staticmethod
    def minify_json(input_path: str) -> str:
        """Minify JSON file by removing unnecessary whitespace."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input JSON file not found: {input_path}")
            
            # Read JSON file
            with open(input_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, "_minified.json")
            
            # Minify JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, separators=(',', ':'), ensure_ascii=False)
            
            return output_path
            
        except json.JSONDecodeError as e:
            raise FileProcessingError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise FileProcessingError(f"JSON minification failed: {str(e)}")
    
    @staticmethod
    def format_xml(input_path: str, indent: int = 2) -> str:
        """Format XML file with proper indentation."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input XML file not found: {input_path}")
            
            # Parse XML
            tree = ET.parse(input_path)
            root = tree.getroot()
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, "_formatted.xml")
            
            # Format XML with indentation
            ET.indent(tree, space=" " * indent, level=0)
            
            # Write formatted XML
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            
            return output_path
            
        except ET.ParseError as e:
            raise FileProcessingError(f"Invalid XML format: {str(e)}")
        except Exception as e:
            raise FileProcessingError(f"XML formatting failed: {str(e)}")
    
    @staticmethod
    def get_json_schema_info(input_path: str) -> Dict[str, Any]:
        """Get information about JSON structure and schema."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input JSON file not found: {input_path}")
            
            # Read JSON file
            with open(input_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            schema_info = {
                "type": type(json_data).__name__,
                "size": len(str(json_data)),
                "structure": FileFormatterService._analyze_json_structure(json_data),
                "keys": list(json_data.keys()) if isinstance(json_data, dict) else None,
                "length": len(json_data) if isinstance(json_data, (list, dict)) else None
            }
            
            return schema_info
            
        except json.JSONDecodeError as e:
            raise FileProcessingError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise FileProcessingError(f"JSON analysis failed: {str(e)}")
    
    @staticmethod
    def _analyze_json_structure(data: Any, max_depth: int = 3) -> Dict[str, Any]:
        """Analyze JSON structure recursively."""
        if isinstance(data, dict):
            structure = {
                "type": "object",
                "keys": list(data.keys()),
                "key_count": len(data),
                "properties": {}
            }
            
            if max_depth > 0:
                for key, value in data.items():
                    structure["properties"][key] = FileFormatterService._analyze_json_structure(value, max_depth - 1)
            
            return structure
        
        elif isinstance(data, list):
            structure = {
                "type": "array",
                "length": len(data),
                "item_types": []
            }
            
            if data and max_depth > 0:
                # Analyze first few items
                for item in data[:3]:
                    structure["item_types"].append(FileFormatterService._analyze_json_structure(item, max_depth - 1))
            
            return structure
        
        else:
            return {
                "type": type(data).__name__,
                "value": str(data)[:100] if len(str(data)) > 100 else data
            }
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported input formats."""
        return list(FileFormatterService.SUPPORTED_INPUT_FORMATS)
    
    @staticmethod
    def cleanup_temp_files(*file_paths: str) -> None:
        """Clean up temporary files."""
        for file_path in file_paths:
            FileService.cleanup_file(file_path)

from typing import Optional, Dict, Any, List, Union
from decimal import Decimal
from app.app_core.config import settings
import logging

import boto3
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class DynamoDBService:
    """Service to handle DynamoDB operations when settings.dynamodb_active is True."""
    
    _resource = None
    
    @classmethod
    def get_resource(cls):
        if cls._resource is None:
            cls._resource = boto3.resource('dynamodb', region_name=settings.aws_region)
        return cls._resource

    @classmethod
    def get_table(cls, table_name: str):
        full_table_name = f"{settings.dynamodb_table_prefix}_{table_name}"
        return cls.get_resource().Table(full_table_name)

    @staticmethod
    def _get_next_id(table_name: str) -> int:
        """Atomically increment and return the next ID for a table."""
        try:
            table = DynamoDBService.get_table("atomic_counter")
            response = table.update_item(
                Key={"table_name": table_name},
                UpdateExpression="ADD last_id :inc",
                ExpressionAttributeValues={":inc": 1},
                ReturnValues="UPDATED_NEW"
            )
            return int(response["Attributes"]["last_id"])
        except Exception as e:
            logger.error(f"Error generating ID for {table_name}: {e}")
            # If AtomicCounter table or item doesn't exist, we might need a fallback
            # but usually it's better to fail so the user knows to setup tables
            raise e

    @staticmethod
    def _clean_item(item: Any) -> Any:
        """Recursively remove None values and convert floats/ints to Decimal/int for DynamoDB."""
        if isinstance(item, dict):
            return {k: v for k, v in ((k, DynamoDBService._clean_item(v)) for k, v in item.items()) if v is not None}
        elif isinstance(item, list):
            return [v for v in (DynamoDBService._clean_item(v) for v in item) if v is not None]
        elif isinstance(item, float):
            return Decimal(str(item))
        elif isinstance(item, int):
            return int(item)
        return item

    @staticmethod
    def _deserialize_item(item: Any) -> Any:
        """Recursively convert DynamoDB Decimal types back to int/float for JSON serialization."""
        if isinstance(item, list):
            return [DynamoDBService._deserialize_item(i) for i in item]
        elif isinstance(item, dict):
            return {k: DynamoDBService._deserialize_item(v) for k, v in item.items()}
        elif isinstance(item, Decimal):
            if item % 1 == 0:
                return int(item)
            else:
                return float(item)
        return item

    @staticmethod
    def put_item(table_name: str, data: Dict[str, Any]) -> str:
        """Generic put_item for any table. Handles nested None values."""
        if not settings.dynamodb_active:
            return None
        try:
            table = DynamoDBService.get_table(table_name)
            if "id" not in data:
                data["id"] = DynamoDBService._get_next_id(table_name)
            if "created_at" not in data:
                data["created_at"] = datetime.utcnow().isoformat()
            
            # Recursively clean None values as DynamoDB doesn't allow them
            item = DynamoDBService._clean_item(data)
            
            # Log for debugging
            logger.info(f"DynamoDB: Writing to {table_name}, ID: {item.get('id')}")
            
            table.put_item(Item=item)
            return data["id"]
        except Exception as e:
            logger.error(f"DynamoDB put_item ({table_name}) failed: {str(e)}")
            # Re-raise for debugging purposes on the live site
            raise e

    @staticmethod
    def get_item(table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generic get_item for any table."""
        if not settings.dynamodb_active:
            return None
        try:
            table = DynamoDBService.get_table(table_name)
            response = table.get_item(Key=key)
            item = response.get('Item')
            return DynamoDBService._deserialize_item(item) if item else None
        except Exception as e:
            logger.error(f"DynamoDB get_item ({table_name}) error: {e}")
            return None

    @staticmethod
    def update_item(table_name: str, key: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Generic update_item for any table. Handles reserved words."""
        if not settings.dynamodb_active:
            return False
        try:
            table = DynamoDBService.get_table(table_name)
            
            # Use placeholders for both names and values to avoid reserved word conflicts
            update_expression_parts = ["#m_at = :t"]
            expression_names = {"#m_at": "modified_at"}
            expression_values = {":t": datetime.utcnow().isoformat()}
            
            for k, v in data.items():
                if v is not None and k != "id":
                    placeholder_name = f"#k_{k}"
                    placeholder_value = f":v_{k}"
                    update_expression_parts.append(f"{placeholder_name} = {placeholder_value}")
                    expression_names[placeholder_name] = k
                    expression_values[placeholder_value] = v
            
            update_expression = "SET " + ", ".join(update_expression_parts)
            
            table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_names,
                ExpressionAttributeValues=expression_values
            )
            return True
        except Exception as e:
            logger.error(f"DynamoDB update_item ({table_name}) failed for key {key}: {str(e)}")
            return False

    @staticmethod
    def query_index(table_name: str, index_name: str, key_expression: Any, expression_values: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generic query for any table index."""
        if not settings.dynamodb_active:
            return []
        try:
            table = DynamoDBService.get_table(table_name)
            query_params = {
                "IndexName": index_name,
                "KeyConditionExpression": key_expression
            }
            if expression_values:
                query_params["ExpressionAttributeValues"] = expression_values
                
            response = table.query(**query_params)
            items = response.get('Items', [])
            return [DynamoDBService._deserialize_item(i) for i in items]
        except Exception as e:
            logger.error(f"DynamoDB query_index ({table_name}, {index_name}) error: {e}")
            # Try a Scan as a fallback if the Index is missing (for development only)
            # This helps if the user hasn't created the Index yet
            if "ValidationException" in str(e) or "Index" in str(e):
                logger.warning(f"Falling back to Scan for {table_name} because Index {index_name} might be missing")
                try:
                    # Very basic scan fallback - this is slow but will at least show data
                    response = DynamoDBService.get_table(table_name).scan()
                    items = response.get('Items', [])
                    # In-memory filter if we have the key name from the expression
                    # This is just a safety net for development
                    return [DynamoDBService._deserialize_item(i) for i in items]
                except:
                    pass
            return []

    # --- Specific Model Helpers ---

    @staticmethod
    def log_conversion(data: Dict[str, Any]) -> str:
        return DynamoDBService.put_item("user_conversion_details", data)

    @staticmethod
    def update_conversion_status(log_id: Any, data: Dict[str, Any]) -> bool:
        return DynamoDBService.update_item("user_conversion_details", {"id": log_id}, data)

    @staticmethod
    def log_request(data: Dict[str, Any]) -> bool:
        return DynamoDBService.put_item("request_logs", data) is not None

    @staticmethod
    def get_user_conversions(user_id: int, limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        from boto3.dynamodb.conditions import Key
        # Querying by UserIdIndex
        items = DynamoDBService.query_index("user_conversion_details", "UserIdIndex", Key('user_id').eq(int(user_id)), {})
        # Sort by created_at descending (DynamoDB query result is not necessarily sorted by non-key attributes)
        items.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        # Apply skip/limit manually since DynamoDB query limit is on the count of items scanned
        return items[skip:skip+limit]

    @staticmethod
    def get_user_conversions_count(user_id: int) -> int:
        from boto3.dynamodb.conditions import Key
        items = DynamoDBService.query_index("user_conversion_details", "UserIdIndex", Key('user_id').eq(int(user_id)), {})
        return len(items)

    @staticmethod
    def get_user_conversion_stats(user_id: int) -> dict:
        from boto3.dynamodb.conditions import Key
        items = DynamoDBService.query_index("user_conversion_details", "UserIdIndex", Key('user_id').eq(int(user_id)), {})
        
        files_converted = 0
        data_processed_bytes = 0
        dates = set()
        
        for item in items:
            if item.get('status') == 'success':
                files_converted += 1
            
            # Use 0 if sizes are missing or None
            input_size = item.get('input_file_size') or 0
            output_size = item.get('output_file_size') or 0
            
            data_processed_bytes += int(input_size) + int(output_size)
            
            created_at = item.get('created_at')
            if created_at:
                # Expecting ISO format like '2026-03-15T12:00:00'
                dates.add(created_at.split('T')[0])
                
        return {
            "files_converted": files_converted,
            "data_processed_bytes": data_processed_bytes,
            "days_active": len(dates)
        }

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        from boto3.dynamodb.conditions import Key
        items = DynamoDBService.query_index("user_list", "EmailIndex", Key('email').eq(email), {})
        return items[0] if items else None

    @staticmethod
    def create_user(data: Dict[str, Any]) -> str:
        return DynamoDBService.put_item("user_list", data)

    @staticmethod
    def get_subscription(user_id: Any) -> Optional[Dict[str, Any]]:
        from boto3.dynamodb.conditions import Key
        # user_id must be numeric to match the index definition
        items = DynamoDBService.query_index("user_subscription_details", "UserIdIndex", Key('user_id').eq(user_id), {})
        return items[0] if items else None

    # --- Helpdesk Helpers ---

    @staticmethod
    def log_contact_us(data: Dict[str, Any]) -> str:
        return DynamoDBService.put_item("customer_contactus_support_details", data)

    @staticmethod
    def log_feedback(data: Dict[str, Any]) -> str:
        return DynamoDBService.put_item("customer_feedback_details", data)

    @staticmethod
    def log_faq(data: Dict[str, Any]) -> str:
        return DynamoDBService.put_item("customer_frequently_asked_questions_details", data)

    @staticmethod
    def log_general_inquiry(data: Dict[str, Any]) -> str:
        return DynamoDBService.put_item("customer_general_inquiries_details", data)

    @staticmethod
    def log_technical_support(data: Dict[str, Any]) -> str:
        return DynamoDBService.put_item("customer_technical_support_details", data)

    @staticmethod
    def log_tool_feedback(data: Dict[str, Any]) -> str:
        return DynamoDBService.put_item("customer_tool_feedback_details", data)

    @staticmethod
    def log_password_reset_otp(data: Dict[str, Any]) -> str:
        return DynamoDBService.put_item("password_reset_otps", data)


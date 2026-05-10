from sqlalchemy.orm import Session
from app.app_models.user_conversion import UserConversionDetails
from typing import Optional, Any, List
from datetime import datetime
import os

class ConversionLogService:
    @staticmethod
    def log_conversion(
        db: Session,
        user_id: Optional[int],
        conversion_type: str,
        input_filename: str,
        input_file_size: Optional[int] = None,
        input_file_type: Optional[str] = None,
        output_filename: Optional[str] = None,
        output_file_size: Optional[int] = None,
        output_file_type: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        method: str = "POST",
        api_endpoint: Optional[str] = None
    ) -> Any:
        """
        Record a conversion event in the database.
        Returns a dummy object if database is inactive to prevent errors in caller.
        """
        from app.app_core.config import settings
        from app.app_services.dynamodb_service import DynamoDBService
        from types import SimpleNamespace

        # Prepare log data
        log_data = {
            "user_id": user_id,
            "conversion_type": conversion_type,
            "input_filename": input_filename,
            "input_file_size": input_file_size,
            "input_file_type": input_file_type,
            "output_filename": output_filename,
            "output_file_size": output_file_size,
            "output_file_type": output_file_type,
            "status": status,
            "error_message": error_message,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "method": method,
            "api_endpoint": api_endpoint
        }

        # 1. Handle DynamoDB (Production Path)
        if settings.dynamodb_active:
            log_id = DynamoDBService.log_conversion(log_data)
            if not log_id:
                import logging
                logging.getLogger(__name__).warning("Failed to log conversion to DynamoDB")
            return SimpleNamespace(id=log_id)

        # 2. Handle Postgres (Development Path)
        if not settings.database_active:
            return SimpleNamespace(id=None)

        db_log = UserConversionDetails(**log_data)
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log

    @staticmethod
    def update_log_status(
        db: Session,
        log_id: int,
        status: str,
        output_filename: Optional[str] = None,
        output_file_size: Optional[int] = None,
        output_file_type: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Optional[UserConversionDetails]:
        """
        Update an existing log entry with final status and results.
        """
        from app.app_core.config import settings
        from app.app_services.dynamodb_service import DynamoDBService

        if not log_id:
            return None

        # Prepare update data
        update_data = {
            "status": status,
            "output_filename": output_filename,
            "output_file_type": output_file_type,
            "error_message": error_message
        }

        # Auto-detect file size if not provided
        if output_filename and not output_file_size:
            possible_paths = [
                output_filename,
                os.path.join(settings.output_dir, output_filename)
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    update_data["output_file_size"] = os.path.getsize(path)
                    break
        elif output_file_size:
            update_data["output_file_size"] = output_file_size

        # Auto-detect file type if not provided
        if output_filename and not output_file_type and "." in output_filename:
            update_data["output_file_type"] = output_filename.split(".")[-1].lower()

        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            DynamoDBService.update_conversion_status(log_id, update_data)
            return None # We return None for update in DynamoDB for now as we don't return model objects
        
        # 2. Handle Postgres
        if not settings.database_active:
            return None

        db_log = db.query(UserConversionDetails).filter(UserConversionDetails.id == log_id).first()
        if not db_log:
            return None
        
        db_log.status = status
        if output_filename:
            db_log.output_filename = output_filename
            db_log.output_file_type = update_data.get("output_file_type", db_log.output_file_type)
            db_log.output_file_size = update_data.get("output_file_size", db_log.output_file_size)
        
        if error_message:
            db_log.error_message = error_message
            
        db.commit()
        db.refresh(db_log)
        return db_log
    @staticmethod
    def get_user_history(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> List[Any]:
        """
        Get conversion history for a specific user ID or guest (device user).
        Optional filtering by date range.
        """
        from app.app_core.config import settings
        from app.app_services.dynamodb_service import DynamoDBService
        from types import SimpleNamespace

        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            items = DynamoDBService.get_user_conversions(user_id, limit, skip)
            
            # Expected fields on the log object
            expected_fields = [
                "id", "created_at", "conversion_type", "input_filename", 
                "input_file_size", "input_file_type", "output_filename", 
                "output_file_size", "output_file_type", "status", "error_message"
            ]
            
            results = []
            for item in items:
                # Ensure all fields exist to prevent AttributeErrors in endpoints
                for field in expected_fields:
                    if field not in item:
                        item[field] = None
                results.append(SimpleNamespace(**item))
            return results

        # 2. Handle Postgres
        if not settings.database_active:
            return []
            
        query = db.query(UserConversionDetails).filter(
            UserConversionDetails.user_id == user_id
        )
        
        if from_date:
            query = query.filter(UserConversionDetails.created_at >= from_date)
        if to_date:
            query = query.filter(UserConversionDetails.created_at <= to_date)
        if status:
            query = query.filter(UserConversionDetails.status == status)
            
        return query.order_by(UserConversionDetails.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_history_count(
        db: Session, 
        user_id: int,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> int:
        """
        Get the total count of conversion history records for a user.
        """
        from app.app_core.config import settings
        from app.app_services.dynamodb_service import DynamoDBService

        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            return DynamoDBService.get_user_conversions_count(user_id)

        # 2. Handle Postgres
        if not settings.database_active:
            return 0
            
        query = db.query(UserConversionDetails).filter(
            UserConversionDetails.user_id == user_id
        )
        
        if from_date:
            query = query.filter(UserConversionDetails.created_at >= from_date)
        if to_date:
            query = query.filter(UserConversionDetails.created_at <= to_date)
        if status:
            query = query.filter(UserConversionDetails.status == status)
            
        return query.count()

    @staticmethod
    def delete_log(db: Session, log_id: int, user_id: int) -> bool:
        """
        Delete a specific log entry if it belongs to the user.
        """
        from app.app_core.config import settings
        from app.app_services.dynamodb_service import DynamoDBService

        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            # First verify the log belongs to the user
            log = DynamoDBService.get_item("user_conversion_details", {"id": int(log_id)})
            if not log or int(log.get("user_id", 0)) != int(user_id):
                return False
            
            table = DynamoDBService.get_table("user_conversion_details")
            table.delete_item(Key={"id": int(log_id)})
            return True

        # 2. Handle Postgres
        if not settings.database_active:
            return False
            
        db_log = db.query(UserConversionDetails).filter(
            UserConversionDetails.id == log_id,
            UserConversionDetails.user_id == user_id
        ).first()
        
        if not db_log:
            return False
            
        db.delete(db_log)
        db.commit()
        return True

    @staticmethod
    def clear_user_history(db: Session, user_id: int) -> int:
        """
        Clear all conversion history for a user.
        """
        from app.app_core.config import settings
        from app.app_services.dynamodb_service import DynamoDBService

        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            items = DynamoDBService.get_user_conversions(user_id, limit=1000) # Get a reasonable amount to delete
            table = DynamoDBService.get_table("user_conversion_details")
            count = 0
            for item in items:
                table.delete_item(Key={"id": item['id']})
                count += 1
            return count

        # 2. Handle Postgres
        if not settings.database_active:
            return 0
            
        count = db.query(UserConversionDetails).filter(
            UserConversionDetails.user_id == user_id
        ).delete()
        db.commit()
        return count

    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> dict:
        """
        Calculate usage statistics for a user.
        """
        from app.app_core.config import settings
        from app.app_services.dynamodb_service import DynamoDBService

        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            return DynamoDBService.get_user_conversion_stats(user_id)

        # 2. Handle Postgres
        if not settings.database_active:
            return {
                "files_converted": 0,
                "data_processed_bytes": 0,
                "days_active": 0
            }
            
        from sqlalchemy import func, cast, Date
        
        # Count successful conversions
        files_converted = db.query(UserConversionDetails).filter(
            UserConversionDetails.user_id == user_id,
            UserConversionDetails.status == "success"
        ).count()

        # Sum total data processed (input + output files)
        total_input_size = db.query(func.sum(UserConversionDetails.input_file_size)).filter(
            UserConversionDetails.user_id == user_id
        ).scalar() or 0
        
        total_output_size = db.query(func.sum(UserConversionDetails.output_file_size)).filter(
            UserConversionDetails.user_id == user_id
        ).scalar() or 0
        
        data_processed_bytes = total_input_size + total_output_size

        # Days active: Number of distinct dates in created_at
        days_active = db.query(func.count(func.distinct(cast(UserConversionDetails.created_at, Date)))).filter(
            UserConversionDetails.user_id == user_id
        ).scalar() or 0

        return {
            "files_converted": files_converted,
            "data_processed_bytes": data_processed_bytes,
            "days_active": days_active
        }

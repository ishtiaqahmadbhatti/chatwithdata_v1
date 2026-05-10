import logging
from sqlalchemy.orm import Session
from app.app_models.user_list import UserList
from app.app_models.user_subscription import UserSubscriptionDetails
from app.app_models.schemas import UserListCreate, UserListUpdate
from typing import Optional, List, Any
from app.app_services.auth_service import get_password_hash, verify_password
from app.app_core.config import settings
from types import SimpleNamespace
from boto3.dynamodb.conditions import Key
from app.app_services.dynamodb_service import DynamoDBService

logger = logging.getLogger(__name__)


class UserListService:
    @staticmethod
    def _attach_subscription_info(db: Session, user: Any) -> Any:
        """Helper to attach subscription info to user object dynamically."""
        if not user:
            return user
        
        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            # For DynamoDB, user is a dict or a SimpleNamespace
            user_id = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
            if user_id:
                try:
                    # No longer converting to str() - use numeric ID
                    sub = DynamoDBService.get_subscription(user_id)
                    if sub:
                        if isinstance(user, dict):
                            user["is_premium"] = sub.get("is_premium", False)
                            user["subscription_plan"] = sub.get("subscription_plan", "free")
                            user["subscription_expiry"] = sub.get("subscription_expiry")
                        else:
                            user.is_premium = sub.get("is_premium", False)
                            user.subscription_plan = sub.get("subscription_plan", "free")
                            user.subscription_expiry = sub.get("subscription_expiry")
                except Exception as e:
                    print(f"Warning: Failed to fetch subscription for {user_id}: {e}")
            return user
        
        # ...rest of the method...

        # 2. Handle Postgres
        if not db:
            return user
            
        from app.app_models.user_subscription import UserSubscriptionDetails
        sub = db.query(UserSubscriptionDetails).filter(UserSubscriptionDetails.user_id == user.id).first()
        
        # dynamic attachment for Pydantic compatibility
        if sub:
            user.is_premium = sub.is_premium
            user.subscription_plan = sub.subscription_plan
            user.subscription_expiry = sub.subscription_expiry
        else:
            user.is_premium = False
            user.subscription_plan = 'free'
            user.subscription_expiry = None
            
        return user

    @staticmethod
    def get_user(db: Session, user_id: Any) -> Optional[Any]:
        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            # Cast to int for DynamoDB numeric key
            user_data = DynamoDBService.get_item("user_list", {"id": int(user_id)})
            if user_data:
                user = SimpleNamespace(**user_data)
                return UserListService._attach_subscription_info(None, user)
            return None

        # 2. Handle Postgres
        if not db:
            return None
        user = db.query(UserList).filter(UserList.id == user_id).first()
        return UserListService._attach_subscription_info(db, user)

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[Any]:
        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            user_data = DynamoDBService.get_user_by_email(email)
            if user_data:
                user = SimpleNamespace(**user_data)
                return UserListService._attach_subscription_info(None, user)
            return None

        # 2. Handle Postgres
        if not db:
            return None
        user = db.query(UserList).filter(UserList.email == email).first()
        return UserListService._attach_subscription_info(db, user)

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[Any]:
        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            user_data = DynamoDBService.get_user_by_email(email)
            if user_data and verify_password(password, user_data.get("password", "")):
                user = SimpleNamespace(**user_data)
                return UserListService._attach_subscription_info(None, user)
            return None

        # 2. Handle Postgres
        if not db:
            return None
        user = db.query(UserList).filter(UserList.email == email).first()
        if user and verify_password(password, user.password):
            return UserListService._attach_subscription_info(db, user)
        return None

    @staticmethod
    def get_user_by_device_id(db: Session, device_id: str) -> Optional[Any]:
        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            items = DynamoDBService.query_index("user_list", "DeviceIdIndex", Key('device_id').eq(device_id), {})
            if items:
                user = SimpleNamespace(**items[0])
                return UserListService._attach_subscription_info(None, user)
            return None

        # 2. Handle Postgres
        if not db:
            return None
        user = db.query(UserList).filter(UserList.device_id == device_id).first()
        return UserListService._attach_subscription_info(db, user)

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[Any]:
        # 1. Handle DynamoDB (Note: skip/limit not natively supported without scan/query)
        if settings.dynamodb_active:
            # For simplicity, we scan. Production should use query or different strategy
            items = DynamoDBService.get_table("user_list").scan(Limit=limit).get('Items', [])
            users = [SimpleNamespace(**item) for item in items]
            for user in users:
                UserListService._attach_subscription_info(None, user)
            return users

        # 2. Handle Postgres
        if not db:
            return []
        users = db.query(UserList).offset(skip).limit(limit).all()
        for user in users:
            UserListService._attach_subscription_info(db, user)
        return users

    @staticmethod
    def create_user(db: Session, user_in: UserListCreate) -> Any:
        user_data = user_in.model_dump()
        user_data["password"] = get_password_hash(user_data["password"])
        
        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            # Check if a guest user with this device_id already exists
            # (same logic as PostgreSQL path — upgrade guest instead of creating new row)
            device_id = user_data.get("device_id")
            if device_id:
                existing_items = DynamoDBService.query_index(
                    "user_list", "DeviceIdIndex", Key('device_id').eq(device_id), {}
                )
                if existing_items:
                    existing = existing_items[0]
                    # Only upgrade if it's a true guest (no email yet)
                    if not existing.get("email"):
                        existing_id = existing["id"]
                        update_data = {
                            "email":        user_data.get("email"),
                            "password":     user_data["password"],
                            "first_name":   user_data.get("first_name"),
                            "last_name":    user_data.get("last_name"),
                            "gender":       user_data.get("gender"),
                            "phone_number": user_data.get("phone_number"),
                        }
                        DynamoDBService.update_item("user_list", {"id": existing_id}, update_data)

                        # Update subscription if it already exists, create only if missing
                        sub_plan = user_data.get("subscription_plan", "free")
                        sub_premium = user_data.get("is_premium", False)
                        existing_sub = DynamoDBService.get_subscription(existing_id)
                        if existing_sub:
                            # Subscription row already created by create_guest_user — just update it
                            DynamoDBService.update_item(
                                "user_subscription_details",
                                {"id": existing_sub["id"]},
                                {"is_premium": sub_premium, "subscription_plan": sub_plan}
                            )
                        else:
                            # No subscription yet — create one
                            DynamoDBService.put_item("user_subscription_details", {
                                "user_id":           existing_id,
                                "is_premium":        sub_premium,
                                "subscription_plan": sub_plan,
                            })

                        existing.update(update_data)
                        existing["id"] = existing_id
                        user = SimpleNamespace(**existing)
                        return UserListService._attach_subscription_info(None, user)

            # No guest found — create a brand new user
            user_id = DynamoDBService.create_user(user_data)
            if user_id:
                user_data["id"] = user_id
                user = SimpleNamespace(**user_data)
                return UserListService._attach_subscription_info(None, user)
            return None

        # 2. Handle Postgres
        if not db:
            return None
            
        # Debug logging
        print(f"DEBUG: create_user called with email={user_in.email}, device_id={user_in.device_id}")
        
        # Check if we have a guest user with this device_id
        if user_in.device_id:
            existing_user = db.query(UserList).filter(UserList.device_id == user_in.device_id).first()
            
            # Only upgrade if it's a guest (no email)
            if existing_user and existing_user.email is None:
                # Update existing guest to registered user
                existing_user.email = user_in.email
                existing_user.password = get_password_hash(user_in.password) if user_in.password else None
                existing_user.first_name = user_in.first_name
                existing_user.last_name = user_in.last_name
                existing_user.gender = user_in.gender
                existing_user.phone_number = user_in.phone_number
                
                # Update subscription explicitly
                sub = db.query(UserSubscriptionDetails).filter(UserSubscriptionDetails.user_id == existing_user.id).first()
                if sub:
                    if user_in.is_premium is not None:
                        sub.is_premium = user_in.is_premium
                    if user_in.subscription_plan:
                        sub.subscription_plan = user_in.subscription_plan
                    db.add(sub)
                else:
                     # Create if missing
                    new_sub = UserSubscriptionDetails(
                        user_id=existing_user.id,
                        is_premium=user_in.is_premium if user_in.is_premium else False,
                        subscription_plan=user_in.subscription_plan if user_in.subscription_plan else 'free',
                        subscription_expiry=user_in.subscription_expiry
                    )
                    db.add(new_sub)
                
                db.add(existing_user)
                db.commit()
                db.refresh(existing_user)
                return UserListService._attach_subscription_info(db, existing_user)

        # Normal creation if no guest found
        db_user = UserList(
            email=user_in.email,
            password=get_password_hash(user_in.password) if user_in.password else None,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            gender=user_in.gender,
            phone_number=user_in.phone_number,
            device_id=user_in.device_id
        )
        db.add(db_user)
        db.flush() # Flush to get ID
        
        # Create subscription details
        subscription = UserSubscriptionDetails(
            user_id=db_user.id,
            is_premium=user_in.is_premium if user_in.is_premium else False,
            subscription_plan=user_in.subscription_plan if user_in.subscription_plan else 'free',
            subscription_expiry=user_in.subscription_expiry
        )
        db.add(subscription)
        
        db.commit()
        db.refresh(db_user)
        return UserListService._attach_subscription_info(db, db_user)

    @staticmethod
    def create_guest_user(db: Session, device_id: str) -> Any:
        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            try:
                user_data = {"device_id": device_id}
                user_id = DynamoDBService.put_item("user_list", user_data)
                if user_id:
                    # Create default subscription
                    subscription_data = {
                        "user_id": user_id,
                        "is_premium": False,
                        "subscription_plan": "free"
                    }
                    DynamoDBService.put_item("user_subscription_details", subscription_data)
                    
                    user_data["id"] = user_id
                    user = SimpleNamespace(**user_data)
                    return UserListService._attach_subscription_info(None, user)
                else:
                    logger.error(f"DynamoDB: Failed to create user in UserList for device_id: {device_id}")
                    return None
            except Exception as e:
                logger.error(f"DynamoDB: Unexpected error in create_guest_user: {e}")
                import traceback
                logger.error(traceback.format_exc())
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=500, 
                    detail={
                        "error_type": "DynamoDBError",
                        "message": str(e),
                        "table": "UserList"
                    }
                )

        # 2. Handle Postgres
        if not db:
            return None
            
        db_user = UserList(
            device_id=device_id
        )
        db.add(db_user)
        db.flush()
        
        from app.app_models.user_subscription import UserSubscriptionDetails
        subscription = UserSubscriptionDetails(
            user_id=db_user.id,
            is_premium=False,
            subscription_plan='free'
        )
        db.add(subscription)
        
        db.commit()
        db.refresh(db_user)
        return UserListService._attach_subscription_info(db, db_user)

    @staticmethod
    def upgrade_subscription(db: Session, user_id: Any, plan_id: str) -> Optional[Any]:
        from datetime import datetime, timedelta
        
        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            sub = DynamoDBService.get_subscription(user_id)
            
            expiry = None
            if plan_id == 'monthly':
                expiry = (datetime.now() + timedelta(days=30)).isoformat()
            elif plan_id == 'yearly':
                expiry = (datetime.now() + timedelta(days=365)).isoformat()
            
            sub_data = {
                "is_premium": True,
                "subscription_plan": plan_id,
                "subscription_expiry": expiry
            }
            
            if sub:
                # Update existing using its primary key 'id'
                success = DynamoDBService.update_item("user_subscription_details", {"id": sub['id']}, sub_data)
            else:
                # Create new
                sub_data["user_id"] = user_id
                success = DynamoDBService.put_item("user_subscription_details", sub_data) is not None
            
            if success:
                return UserListService.get_user(None, user_id)
            return None

        # 2. Handle Postgres
        if not db:
            return None
            
        db_user = db.query(UserList).filter(UserList.id == user_id).first()
        if not db_user:
            return None
        
        from app.app_models.user_subscription import UserSubscriptionDetails
        sub = db.query(UserSubscriptionDetails).filter(UserSubscriptionDetails.user_id == user_id).first()
        
        if not sub:
            # Create if missing
            sub = UserSubscriptionDetails(user_id=db_user.id, is_premium=False, subscription_plan='free')
            db.add(sub)

        sub.is_premium = True
        sub.subscription_plan = plan_id
        
        # Set expiry based on plan
        if plan_id == 'monthly':
            sub.subscription_expiry = datetime.now() + timedelta(days=30)
        elif plan_id == 'yearly':
            sub.subscription_expiry = datetime.now() + timedelta(days=365)
            
        db.add(sub)
        db.commit()
        db.refresh(db_user)
        return UserListService._attach_subscription_info(db, db_user)

    @staticmethod
    def update_user(db: Session, user_id: Any, user_update: UserListUpdate) -> Any:
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            print(f"DEBUG: update_user hashing password for ID {user_id}")
            update_data["password"] = get_password_hash(update_data["password"])

        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            user_id_int = int(user_id)
            print(f"DEBUG: update_user (DynamoDB) with ID {user_id_int}. Fields: {list(update_data.keys())}")
            success = DynamoDBService.update_item("user_list", {"id": user_id_int}, update_data)
            print(f"DEBUG: DynamoDB update result: {success}")
            if success:
                user_data = DynamoDBService.get_item("user_list", {"id": user_id_int})
                if user_data:
                    user = SimpleNamespace(**user_data)
                    return UserListService._attach_subscription_info(None, user)
            return None

        # 2. Handle Postgres
        if not db:
            return None
        db_user = db.query(UserList).filter(UserList.id == user_id).first()
        if not db_user:
            return None
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
            
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return UserListService._attach_subscription_info(db, db_user)

    @staticmethod
    def delete_user(db: Session, user_id: Any) -> bool:
        # 1. Handle DynamoDB
        if settings.dynamodb_active:
            # Delete from UserList
            table = DynamoDBService.get_table("user_list")
            table.delete_item(Key={"id": int(user_id)})
            
            # Delete from UserSubscription (find by user_id GSI first)
            sub = DynamoDBService.get_subscription(user_id)
            if sub:
                sub_table = DynamoDBService.get_table("user_subscription_details")
                sub_table.delete_item(Key={"id": sub['id']})
            return True

        # 2. Handle Postgres
        if not db:
            return False
            
        from app.app_models.user_subscription import UserSubscriptionDetails
        
        db_user = db.query(UserList).filter(UserList.id == user_id).first()
        if not db_user:
            return False
            
        # Manually delete subscription first (since no cascade)
        db.query(UserSubscriptionDetails).filter(UserSubscriptionDetails.user_id == user_id).delete()
        
        db.delete(db_user)
        db.commit()
        return True

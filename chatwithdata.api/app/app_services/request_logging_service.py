import uuid
from typing import Tuple, Dict, Any, Optional
from fastapi import Request, Response
from datetime import datetime
from app.app_core.database import get_db
from app.app_models.request_log import RequestLog
from sqlalchemy.orm import Session

try:
    from user_agents import parse as parse_ua
except Exception:  # Dependency may not be installed yet during dev
    parse_ua = None


def ensure_client_id_cookie(request: Request, response: Response) -> str:
    client_id = request.cookies.get("client_id")
    if not client_id:
        client_id = uuid.uuid4().hex
        response.set_cookie(
            "client_id",
            client_id,
            max_age=31536000,
            samesite="Lax",
            httponly=False,
        )
    return client_id


def extract_ip(request: Request) -> Tuple[str, str]:
    xff = request.headers.get("x-forwarded-for", "")
    ip = (
        xff.split(",")[0].strip()
        if xff
        else request.client.host if request.client else None
    )
    return ip, xff


def detect_source(request: Request) -> str:
    ua = (request.headers.get("user-agent") or "").lower()
    if "postman" in ua:
        return "postman"
    if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
        return "docs"
    header_platform = (request.headers.get("x-app-platform") or "").lower()
    if header_platform:
        return header_platform
    if "flutter" in ua or "okhttp" in ua or "android" in ua or "iphone" in ua:
        return "mobile"
    if "mozilla" in ua or "chrome" in ua or "safari" in ua:
        return "web"
    return "unknown"


def parse_device_info(user_agent: str):
    if not user_agent or parse_ua is None:
        return "unknown", None, None
    parsed = parse_ua(user_agent)
    device_type = (
        "mobile" if parsed.is_mobile else
        "tablet" if parsed.is_tablet else
        "pc" if parsed.is_pc else
        "bot" if parsed.is_bot else
        "unknown"
    )
    return device_type, parsed.os.family, parsed.browser.family


class RequestLoggingService:
    """Service for logging API requests to the database."""

    # Valid column names on the RequestLog model — used to filter unknown keys
    _VALID_COLUMNS = {
        "client_id", "session_id", "request_id",
        "method", "path", "query_string", "status_code", "latency_ms",
        "source", "ip", "x_forwarded_for", "user_agent", "origin", "referer",
        "device_type", "os", "browser",
        "app_platform", "app_version", "device_id",
        "is_docs", "is_download",
    }

    @staticmethod
    def log_request(
        endpoint: str = None,
        method: str = None,
        user_id: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        status_code: int = 200,
        processing_time: Optional[float] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log a request to the database."""
        from app.app_core.config import settings
        from app.app_services.dynamodb_service import DynamoDBService

        # Build a flat dict from all sources
        raw = {
            "path":        kwargs.get("path") or endpoint,
            "method":      method or kwargs.get("method", "UNKNOWN"),
            "status_code": status_code,
            "ip":          ip_address or kwargs.get("ip"),
            "user_agent":  user_agent or kwargs.get("user_agent"),
            **kwargs,   # middleware passes client_id, session_id, latency_ms, etc.
        }

        # 1. Handle DynamoDB (send raw dict — no column restrictions)
        if settings.dynamodb_active:
            DynamoDBService.log_request(raw)
            return

        # 2. Handle Postgres — filter to known model columns only
        if not settings.database_active:
            return

        try:
            db = next(get_db())

            safe = {k: v for k, v in raw.items() if k in RequestLoggingService._VALID_COLUMNS}
            safe.setdefault("method", "UNKNOWN")
            safe.setdefault("path", "/")

            request_log = RequestLog(**safe)
            db.add(request_log)
            db.commit()

        except Exception as e:
            print(f"Warning: Failed to log request: {str(e)}")
        finally:
            if 'db' in locals():
                db.close()

    @staticmethod
    def log_conversion_request(
        conversion_type: str,
        user_id: Optional[str] = None,
        input_size: int = 0,
        output_size: int = 0,
        success: bool = True,
        error_message: Optional[str] = None,
        processing_time: Optional[float] = None
    ) -> None:
        """Log a conversion request specifically."""
        from app.app_core.config import settings
        from app.app_services.dynamodb_service import DynamoDBService

        # 1. Handle DynamoDB (full data)
        if settings.dynamodb_active:
            DynamoDBService.log_request({
                "endpoint": f"/api/v1/convert/{conversion_type}",
                "method": "POST",
                "user_id": user_id,
                "status_code": 200 if success else 400,
                "processing_time": processing_time,
                "request_data": {"conversion_type": conversion_type},
                "response_data": {
                    "success": success,
                    "input_size": input_size,
                    "output_size": output_size,
                    "error_message": error_message,
                },
            })
            return

        # 2. Handle Postgres
        if not settings.database_active:
            return

        try:
            db = next(get_db())
            request_log = RequestLog(
                method      = "POST",
                path        = f"/api/v1/convert/{conversion_type}",
                status_code = 200 if success else 400,
            )
            db.add(request_log)
            db.commit()
        except Exception as e:
            print(f"Warning: Failed to log conversion request: {str(e)}")
        finally:
            if 'db' in locals():
                db.close()


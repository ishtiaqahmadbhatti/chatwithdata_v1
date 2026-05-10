from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.app_core.database import Base


class RequestLog(Base):
    """HTTP request log for anonymous and authenticated usage tracking."""
    __tablename__ = "smartconverter_request_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Identity and correlation
    client_id = Column(String(64), index=True, nullable=True)
    session_id = Column(String(64), index=True, nullable=True)
    request_id = Column(String(64), index=True, nullable=True)

    # Request context
    method = Column(String(10), nullable=False)
    path = Column(String(512), index=True, nullable=False)
    query_string = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)

    # Source and environment
    source = Column(String(32), index=True, nullable=True)
    ip = Column(String(64), index=True, nullable=True)
    x_forwarded_for = Column(String(256), nullable=True)
    user_agent = Column(Text, nullable=True)
    origin = Column(String(256), nullable=True)
    referer = Column(String(512), nullable=True)

    # Device hints
    device_type = Column(String(32), nullable=True)
    os = Column(String(64), nullable=True)
    browser = Column(String(64), nullable=True)

    # Client-provided metadata (optional)
    app_platform = Column(String(64), nullable=True)
    app_version = Column(String(64), nullable=True)
    device_id = Column(String(128), nullable=True)

    # Flags
    is_docs = Column(Boolean, default=False)
    is_download = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())



from sqlalchemy import Integer, Boolean, DateTime, String, Column, UUID, JSON
from app.models.base_model import BaseModel

from datetime import datetime, timezone

import uuid

class AuthSession(BaseModel):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(String, nullable=False)
    app_id = Column(String, nullable=False)
    key_id = Column(String, nullable=True)  # reference to the API key used
    user_id = Column(String, nullable=True)  # optional, if you want to track user sessions
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    meta_data = Column(JSON)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
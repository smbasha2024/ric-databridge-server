from sqlalchemy import Integer, Boolean, DateTime, String, Column, UUID
from app.models.base_model import BaseModel

import uuid
from datetime import datetime, timezone

class APIKey(BaseModel):
    __tablename__ = "api_keys" 

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(String, nullable=False)
    app_id = Column(String, nullable=False)
    app_name = Column(String)
    key_id = Column(String, unique=True, nullable=False)
    key_hash = Column(String)
    enabled = Column(Boolean, default=False)
    rate_limit = Column(Integer)

    #Audit Fields
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_by = Column(String)
    updated_by = Column(String)
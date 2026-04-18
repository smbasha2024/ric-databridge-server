import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Column, UUID, DateTime
from app.models.base_model import BaseModel

class TenantApp(BaseModel):
    __tablename__ = "tenant_apps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(255), nullable=True)
    app_id = Column(String(255), nullable=True)
    app_name = Column(String(255), nullable=True)
    app_url = Column(String(500), nullable=True)
    app_description = Column(String(1000), nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
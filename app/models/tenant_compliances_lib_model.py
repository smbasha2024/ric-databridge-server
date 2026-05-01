# app/models/tenant_compliances_lib.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Column, UUID, DateTime
from app.models.base_model import BaseModel

class TenantComplianceLib(BaseModel):
    __tablename__ = "tenant_compliances_lib"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(255), nullable=True)
    app_id = Column(String(255), nullable=True)
    category = Column(String(255), nullable=True)
    act_name = Column(String(255), nullable=True)
    form = Column(String(255), nullable=True)
    purpose = Column(String(500), nullable=True)
    activity_id = Column(String(255), nullable=True)
    activity = Column(String(500), nullable=True)
    ricago_section_id = Column(String(255), nullable=True)
    frequency = Column(String(255), nullable=True)
    due_date = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
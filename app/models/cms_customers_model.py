# app/models/cms_customers.py
import uuid
from sqlalchemy import String, Column, UUID, DateTime
from app.models.base_model import BaseModel
from datetime import datetime, timezone

class CMSCustomer(BaseModel):
    __tablename__ = "cms_customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(255), nullable=True)
    app_id = Column(String(255), nullable=True)
    tenant_name= Column(String(255), nullable=True)
    tenant_url = Column(String(500), nullable=True)
    credentials = Column(String(2000), nullable=True)           # JSON string
    credential_managers = Column(String(2000), nullable=True)   # JSON string

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
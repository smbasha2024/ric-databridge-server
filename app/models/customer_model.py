from sqlalchemy import String, Column, UUID, DateTime
from app.models.base_model import BaseModel

import uuid
from datetime import datetime, timezone

class Customer(BaseModel):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(String(255), nullable=True)
    tenant_id = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    city = Column(String(255), nullable=True)
    state = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)

    # Audit fields
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
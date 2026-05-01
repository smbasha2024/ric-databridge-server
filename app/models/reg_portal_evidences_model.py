# app/models/reg_portal_evidences.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Column, UUID, DateTime
from app.models.base_model import BaseModel

class RegPortalEvidence(BaseModel):
    __tablename__ = "reg_portal_evidences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(255), nullable=True)
    tenant_name = Column(String(255), nullable=True)
    app_id = Column(String(255), nullable=True)
    c_name = Column(String(255), nullable=True)
    activity_id = Column(String(255), nullable=True)
    ricago_section_id = Column(String(255), nullable=True)
    financial_year = Column(String(255), nullable=True)
    applicable_month = Column(String(255), nullable=True)
    uid_to_consider = Column(String(255), nullable=True)
    org_uid = Column(String(500), nullable=True)          # JSON string: {"DisplayName":"","Value":""}
    loc_uid = Column(String(500), nullable=True)          # JSON string
    closure_date = Column(String(255), nullable=True)
    doc_id = Column(String(255), nullable=True)
    comments = Column(String(1000), nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
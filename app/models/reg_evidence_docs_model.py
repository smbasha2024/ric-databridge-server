# app/models/reg_evidence_docs.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Column, UUID, DateTime, LargeBinary
from app.models.base_model import BaseModel

class RegEvidenceDoc(BaseModel):
    __tablename__ = "reg_evidence_docs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(255), nullable=False)
    app_id = Column(String(255), nullable=False)
    doc_id = Column(String(255), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_type = Column(String(255), nullable=True)
    #file_stream = Column(String(2000), nullable=True)   # path, URL, or base64
    file_stream =Column(LargeBinary)   
    comments = Column(String(1000), nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
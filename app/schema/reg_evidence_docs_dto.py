# app/dto/reg_evidence_doc_dto.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RegEvidenceDoc(BaseModel):
    id: Optional[str]= None
    tenant_name: Optional[str]= None
    c_name: Optional[str]= None
    doc_id: Optional[str]= None
    file_name: Optional[str]= None
    file_type: Optional[str]= None
    file_stream: Optional[bytes]= None
    comments: Optional[str]= None

    created_at: Optional[datetime]= None
    updated_at: Optional[datetime]= None
    created_by: Optional[str]= None
    updated_by: Optional[str]= None
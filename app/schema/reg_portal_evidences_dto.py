# app/dto/reg_portal_evidence_dto.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RegPortalEvidence(BaseModel):
    id: Optional[str]= None
    tenant_id: Optional[str]= None
    tenant_name: Optional[str]= None
    app_id: Optional[str]= None
    activity_id: Optional[str]= None
    riago_section_id: Optional[str]= None
    financial_year: Optional[str]= None
    applicable_month: Optional[str]= None
    Uid_to_consider: Optional[str]= None
    org_uid: Optional[str]= None            # JSON string: {"DisplayName":"","Value":""}
    Loc_uid: Optional[str]= None            # JSON string
    closure_date: Optional[str]= None
    doc_id: Optional[str]= None
    comments: Optional[str]= None
    created_at: Optional[datetime]= None
    updated_at: Optional[datetime]= None
    created_by: Optional[str]= None
    updated_by: Optional[str]= None
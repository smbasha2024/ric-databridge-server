# app/dto/tenant_compliance_lib_dto.py
from pydantic import BaseModel
from datetime import datetime

class TenantComplianceLib(BaseModel):
    id: str
    tenant_id: str
    app_id: str
    category: str
    act_name: str
    form: str
    purpose: str
    activity_id: str
    activity: str
    ricago_section_id: str
    frequency: str
    due_date: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str
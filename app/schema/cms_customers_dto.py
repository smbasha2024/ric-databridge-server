# app/dto/cms_customer_dto.py
from pydantic import BaseModel
from datetime import datetime

class CMSCustomer(BaseModel):
    id: str
    tenant_id: str
    app_id: str
    tenant_name: str
    tenant_url: str
    credentials: str        # JSON string
    credential_managers: str  # JSON string
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str
# app/dto/tenant_app_dto.py
from pydantic import BaseModel
from datetime import datetime

class TenantApp(BaseModel):
    id: str
    tenant_id: str
    app_id: str
    app_name: str
    app_url: str
    app_description: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str
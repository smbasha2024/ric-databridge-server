from pydantic import BaseModel
from datetime import datetime

class Customer(BaseModel):
    id: str                # UUID as string
    customer_id: str
    tenant_id: str
    company_name: str
    address: str
    city: str
    state: str
    country: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str
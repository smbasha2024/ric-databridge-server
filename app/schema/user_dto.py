#---------------------- PyDantic Models ---------------------------------------
# You cant user entities directly in FastAPI routes, so we use Pydantic models
#------------------------------------------------------------------------------
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: str
    tenant_id: str
    app_id: str
    user_id: str
    user_name: str
    password: str          # In real usage, never return plain password
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

#------------------------------------------------------------------------------
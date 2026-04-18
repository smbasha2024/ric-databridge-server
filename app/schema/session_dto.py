
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

class AuthSession(BaseModel):
    client_id: str
    app_id: str
    key_id: str
    user_id: str
    token: str
    expires_at: datetime
    is_active: bool
    meta_data: Dict[str, Any]
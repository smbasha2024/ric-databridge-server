#---------------------- PyDantic Models ---------------------------------------
# You cant user entities directly in FastAPI routes, so we use Pydantic models
#------------------------------------------------------------------------------
from pydantic import BaseModel
from datetime import datetime

class APIKey(BaseModel):
    key_hash : str
    app_name : str
    app_id : str
    client_id: str
    enabled : bool
    rate_limit : int
    created_at : datetime
#------------------------------------------------------------------------------

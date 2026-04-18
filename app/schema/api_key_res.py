#---------------------- PyDantic Models ---------------------------------------
# You cant user entities directly in FastAPI routes, so we use Pydantic models
#------------------------------------------------------------------------------
from pydantic import BaseModel
from datetime import datetime

class APIKeyRes(BaseModel):
    client_id: str
    app_id : str
    key_id : str
    key_hash : str
    enabled : bool
#------------------------------------------------------------------------------

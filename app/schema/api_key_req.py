#---------------------- PyDantic Models ---------------------------------------
# You cant user entities directly in FastAPI routes, so we use Pydantic models
#------------------------------------------------------------------------------
from pydantic import BaseModel
from datetime import datetime

class APIKeyReq(BaseModel):
    app_id : str
    client_id: str
    client_secret: str
#------------------------------------------------------------------------------

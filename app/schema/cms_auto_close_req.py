#---------------------- PyDantic Models ---------------------------------------
# You cant user entities directly in FastAPI routes, so we use Pydantic models
#------------------------------------------------------------------------------
from pydantic import BaseModel
from datetime import datetime

class CMSAutoCloseReq(BaseModel):
    Clientname: str
    ClientURL: str
    CName: str
    FiscalYear: int
    ApplicableMonth: int
    RicagoSectionID: int
#------------------------------------------------------------------------------
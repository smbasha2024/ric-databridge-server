#---------------------- CREATE Tables -----------------------------------------------------
# Python entitiy classes creates/updates tables directly into the database and access them
#------------------------------------------------------------------------------------------
from sqlalchemy import String, Column, UUID, DateTime
from app.models.base_model import BaseModel

import uuid
from datetime import datetime, timezone

class User(BaseModel):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(255), nullable=True)
    app_id = Column(String(255), nullable=True)
    user_id = Column(String(255), nullable=True)
    user_name = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)  # store hashed password
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
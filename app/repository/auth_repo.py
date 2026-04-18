from app.models.api_keys_model import APIKey  # SQLAlchemy model for api_keys table
from app.models.sessions_model import AuthSession  # SQLAlchemy model for sessions table

from typing import Optional
from sqlalchemy import select, desc
from datetime import datetime, timezone

# ---------------------- Repository (DB calls) ---------------------- #
class AuthRepository:
    """Handles all database interactions for authentication."""

    def __init__(self, db):
        self.db = db

    async def save_api_key(self, client_id: str, app_id: str, app_name: str, key_id: str, key_hash: str, rate_limit: int = 1000) -> APIKey:
        existing_key = self.db.query(APIKey).filter(APIKey.key_id == key_id).first()
        
        if existing_key:
            # Update the existing record
            existing_key.key_hash = key_hash
            existing_key.enabled = True
            existing_key.rate_limit = rate_limit
            # Optional: update timestamp if you have an updated_at column
            existing_key.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(existing_key)

            return existing_key
        else:
            # Create a new record
            new_key = APIKey(
                client_id=client_id,
                app_id=app_id,
                app_name=app_name,
                key_id=key_id,
                key_hash=key_hash,
                enabled=True,
                rate_limit=rate_limit,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            self.db.add(new_key)
            self.db.commit()
            self.db.refresh(new_key)

            return new_key
    
    def get_api_key_by_client_app(self, client_id: str, app_id: str) -> APIKey | None:
        """
        Retrieve an API key record by client_id and app_id.
        Returns the APIKey object if found, otherwise None.
        """
        api_key = self.db.query(APIKey).filter(
            APIKey.client_id == client_id,
            APIKey.app_id == app_id
        ).first()

        return api_key

    async def get_api_key_by_hash(self, hashed_key: str) -> Optional[APIKey]:
        """Retrieve an API key record by its hash."""
        try:
            result = self.db.execute(
                select(APIKey).where(APIKey.key_hash == hashed_key)
            )
        except Exception as err:
            print(f"############# DB Error: {err}")
            raise err
        
        #print(f"############# DB Result: {result}")
        return result.scalar_one_or_none()

    async def save_session(self, token: str, client_id: str, app_id: str, key_id: str | None, user_id: str | None, expires_at: datetime) -> AuthSession:
        new_session = AuthSession(
            token=token,
            client_id=client_id,
            app_id=app_id,
            key_id=key_id,
            user_id=user_id,
            expires_at=expires_at
        )
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        
        return new_session

    async def get_session_by_client_app(self, tenant_id: str, app_id: str, session_token: str) -> Optional[AuthSession]:
        """Retrieve a session record by its token."""

        stmt = select(AuthSession).where(
            AuthSession.client_id == tenant_id,
            AuthSession.app_id == app_id,
            AuthSession.token == session_token)
        
        # Order by latest expiry
        stmt = stmt.order_by(desc(AuthSession.expires_at)).limit(1)

        result = self.db.execute(stmt)

        return result.scalar_one_or_none()
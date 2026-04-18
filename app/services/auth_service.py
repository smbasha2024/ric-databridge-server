from app.repository.auth_repo import AuthRepository
from app.schema.api_key_dto import APIKey
from app.schema.session_dto import AuthSession as AuthSessionDTO

from app.auth.auth import generate_api_key, get_hash_key, create_access_token

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import hashlib
import base64
import binascii

# ---------------------- Service (business logic) ---------------------- #
class AuthService:
    """Encapsulates authentication business logic."""

    def __init__(self, repo: AuthRepository):
        self.repo = repo

    def hash_key(self, key: str) -> str:
        """Hash an API key using SHA-256."""
        return hashlib.sha256(key.encode()).hexdigest()

    
    async def generate_app_api_key(self, client_id: str, app_id: str, client_secret: str, key_length: int = 32):
        key_result = generate_api_key(client_id, app_id, client_secret, random_bytes  = key_length)
        result = await self.repo.save_api_key(
            client_id=key_result["client_id"],
            app_id=key_result["app_id"],
            app_name=f"{key_result['client_id']}_{key_result['app_id']}",
            key_id=f"{client_id}_{app_id}", 
            key_hash=key_result["key_hash"],
            rate_limit=1000
        )   
        result.raw_key = encoded_key = base64.b64encode(key_result["raw_key"].encode('utf-8')).decode('utf-8')   # Attach the raw key to the result for returning to client
        return result

    async def validate_api_key_by_client_app(self, ecoded_api_key: str, client_id: str, app_id: str) -> APIKey:
        """
        Validate the provided raw API key against the stored hash.
        Returns the APIKey object if valid, else raises HTTPException.
        """
        # Hash the incoming raw API key using the same algorithm used when storing
        # (assuming SHA-256 based on earlier logs)
        try:
            raw_api_key = base64.b64decode(ecoded_api_key.encode('utf-8')).decode('utf-8') # Decode the raw key from base64
        except (binascii.Error, UnicodeDecodeError):
            raise HTTPException(
                status_code=400,
                detail={
                    "status": False,
                    "error_code": 400,
                    "error_desc": "Invalid API Key format. Expected Base64 encoded key."
                }
            )
        #print (f"################ Decoded API Key: {raw_api_key} ################")
        hashed_key = get_hash_key(raw_api_key) #hashlib.sha256(raw_api_key.encode()).hexdigest()
        #print(f"################ Hashed API Key for validation: {hashed_key} ################")
        
        # Retrieve the key record for this client/app
        key_record = self.repo.get_api_key_by_client_app(client_id, app_id)
        #print(f"################ Stored API Key for validation: {key_record.key_hash} ################")

        if not key_record:
            raise HTTPException(status_code=401, detail="No record found for the provided Tenant ID and App ID and API Key")
        
        # Compare hashes
        if key_record.key_hash != hashed_key:
            raise HTTPException(status_code=401, detail="Invalid API key: Hash mismatch")
        
        # Check if enabled
        if not key_record.enabled:
            raise HTTPException(status_code=403, detail="API key is disabled")
        
        
        return key_record

    async def generate_auth_token_by_client_app(self, client_id: str, app_id: str, aud_url:str, key_id: str, user_id:str = None) -> AuthSessionDTO:
        access_token, expires_at = create_access_token(client_id, app_id, aud_url, key_id) # Create JWT token for the session

        auth_session = await self.repo.save_session(
            token=access_token,
            client_id=client_id,
            app_id=app_id,
            key_id=key_id,
            user_id=user_id,  # No user context in this flow
            expires_at=expires_at
        )
        return auth_session

    async def validate_api_key(self, api_key: str) -> APIKey:
        """Validate an API key (hash + enabled). Returns the key object or raises."""
        hashed = self.hash_key(api_key)
        key = await self.repo.get_api_key_by_hash(hashed)
        print(f"################ Hashed API Key: {hashed} and key: {key} ################")

        if not key:
            result = {
                    "status" : status.HTTP_403_FORBIDDEN, 
                    "detail" :{"status": False, "error_code": 401, "error_desc": "Tenant ID, App ID and API Keys are mandory. Should be supplied as part of request header. One or all are missing."}
                }
            return result
                
        
        """
        if not key.enabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="API key disabled"
            )
        """
        return key

    async def validate_auth_token_by_client_app(self, tenant_id: str, app_id: str, session_token: str) -> AuthSessionDTO:
        """Validate a session token (exists + not expired). Returns the session or raises."""
        session = await self.repo.get_session_by_client_app(tenant_id, app_id, session_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found"
            )
        if session.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired"
            )
        return session
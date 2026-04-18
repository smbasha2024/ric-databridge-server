import uuid

from app.configs.settings import settings

from fastapi import HTTPException, status, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

import jwt
from datetime import datetime, timedelta, timezone

import hashlib
import secrets
from typing import Optional, Dict, Any

def _hash_raw_api_key(raw_key: str, pepper: str = "") -> str:
    """
    Hash a raw API key using SHA-256 with an optional pepper.
    The pepper adds an extra server‑side secret (e.g., ricago_secret).
    """
    # Combine key with pepper to strengthen hash
    key_with_pepper = raw_key + pepper
    #print(f"################ Hashing API Key with pepper. {key_with_pepper} ################")
    return hashlib.sha256(key_with_pepper.encode('utf-8')).hexdigest()

def get_hash_key(raw_key: str) -> str:
    raw_key_with_pepper = raw_key + settings.server.api_secret_key
    #print(f"################ Getting hash for API Key with pepper. {raw_key_with_pepper} ################")
    return hashlib.sha256(raw_key_with_pepper.encode('utf-8')).hexdigest()

def generate_api_key(client_id: str, app_id: str, client_secret: str,random_bytes: int = 32) -> Dict[str, Any]:
    """
    Create a new static API key.
    
    Args:
        client_id: Client identifier.
        app_id: Application identifier.
        ricago_secret: Server‑side secret (pepper) from settings.
        client_secret: Client’s own secret (e.g., for additional binding).
        random_bytes: Length of random part (default 32 bytes → ~256 bits).
        
    Returns:
        Dictionary containing:
            - raw_key: The plain API key (give this to the client ONCE).
            - key_hash: SHA‑256 hash of the raw key + pepper (store this in DB).
            - client_id, app_id (as provided).
            - created_at: Current UTC timestamp.
    """
    # Generate a cryptographically secure random string
    random_part = secrets.token_urlsafe(random_bytes)
    
    # Optionally include a timestamp to guarantee uniqueness even if random repeats
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Build the raw API key from all inputs + random text
    # You can change the format, but keep it unpredictable
    raw_key = f"{client_id}:{app_id}:{client_secret}:{random_part}:{timestamp}"
    
    # Hash the raw key using the ricago_secret as pepper
    key_hash = _hash_raw_api_key(raw_key, pepper=settings.server.api_secret_key)
    
    return {
        "raw_key": raw_key,
        "key_hash": key_hash,
        "client_id": client_id,
        "app_id": app_id,
        "created_at": datetime.now(timezone.utc)
    }

def create_access_token(client_id: str, app_id: str, aud_url: str, key_id: str) -> str:
    """Create a JWT access token for a given client and API key."""

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.server.token_expire_minutes)
    payload = {
        "sub": str(client_id),
        "key_id": str(key_id),
        "exp": expires_at,
        "iat": datetime.now(timezone.utc),
        "iss": settings.server.token_issuer,
        "aud": aud_url,                         # audience
        "jti": str(uuid.uuid4()),               # unique token ID
        "client_id": str(client_id),            # redundant but explicit
        "app_id": str(app_id),                  # your app identifier
    }
    secret_key = settings.server.token_secret_key   # Combine server secret with client secret for added security
    access_token = jwt.encode(payload, secret_key, algorithm=settings.server.token_algorithm)

    return access_token, expires_at


def verify_token(token: str) -> dict:
    #print(f"Token: {token[:50]}... (length {len(token)})")
    """
    # 1. Try to decode without signature verification
    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
        print("Unverified payload:", unverified)
    except Exception as e:
        print("Token malformed:", e)
        raise HTTPException(403, "Token malformed")
    
    # 2. Verify signature only (no issuer, no audience)
    try:
        payload = jwt.decode(token, settings.server.token_secret_key, algorithms=[settings.server.token_algorithm],issuer=settings.server.token_issuer,audience="ricauth" )
        print("Signature verified, payload:", payload)
    except jwt.InvalidTokenError as e:
        print("Signature verification failed:", e)
        raise HTTPException(403, "Invalid token signature")
    """
    # 3. Now add issuer verification
    try:
        payload = jwt.decode(
            token,
            settings.server.token_secret_key,
            algorithms=[settings.server.token_algorithm],
            issuer=settings.server.token_issuer,
            audience="ricauth"
        )
        #print("Issuer verified:", payload)
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    
    except jwt.InvalidTokenError as e:
        #print("Issuer verification failed:", e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Token. Issuer verification failed."
        )
    # 4. Optionally verify audience (you should)
    # audience = expected_audience_url
    # try:
    #     payload = jwt.decode(..., audience=audience)
    # except jwt.InvalidAudienceError:
    #     raise HTTPException(403, "Invalid audience")
    
    return payload

# ---------------------- Dependency & Middleware ---------------------- #
class AuthMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that validates either an API key (X-API-Key header)
    or a session token (Bearer <JWT>). Attaches the authenticated entity
    to request.state.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public endpoints (e.g., /, /openapi /health, /docs)
        #print(f"################ AuthMiddleware: Processing request for {request.url.path} ################")
        try:
            if request.url.path in settings.server.public_paths:  # define in your settings
                return await call_next(request)

            # 1) Try API key
            api_key = request.headers.get("X-API-Key")
            tenant_id = request.headers.get("X-Tenant-ID")
            app_id = request.headers.get("X-APP-ID")
            
            if not api_key:
                #raise HTTPException(status_code=401, detail="Missing API Key")
                raise HTTPException(
                    status_code=401,
                    detail="Missing API Key"
                )
            if not tenant_id:
                #raise HTTPException(status_code=401, detail="Missing Tenant ID")
                raise HTTPException(
                    status_code=401,
                    detail="Missing Tenant ID"
                )
            if not app_id:
                #raise HTTPException(status_code=401, detail="Missing App ID")
                raise HTTPException(
                    status_code=401,
                    detail="Missing App ID"
                )
            
            if api_key:
                request.state.api_key = api_key
            if tenant_id:
                request.state.tenant_id = tenant_id
            if app_id:
                request.state.app_id = app_id

            if request.url.path in settings.server.app_token_path : #"/ricauth/GetAppAuthToken"
                request.state.auth_type = "api_key"
                return await call_next(request)

            # 2) Try Bearer token (session JWT)
            #print("Now in authorization")
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                #raise HTTPException(status_code=401, detail="Missing Authorization Token")
                raise HTTPException(
                    status_code=401,
                    detail="Missing Authorization Token"
                )
        
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

                payload = verify_token(token)

                request.state.auth_type = "jwt"
                request.state.token = token
                request.state.token_expiry = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
                request.state.jwt_payload = payload

                return await call_next(request)
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid Authorization header format. Bearer token expected. Format should be: Authorization: Bearer <token>"
                )
        except HTTPException as exc:
            # Return a JSON response matching your global error format
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "status": False,
                    "error_code": exc.status_code,
                    "error_desc": exc.detail
                }
            )
        except Exception as exc:
            # Log unexpected errors for debugging
            # logger.exception("Unexpected error in AuthMiddleware")
            return JSONResponse(
                status_code=500,
                content={
                    "status": False,
                    "error_code": 500,
                    "error_desc": "Internal server error"
                }
            )

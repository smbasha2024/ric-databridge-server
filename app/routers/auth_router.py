from fastapi import APIRouter, Depends, Request
from fastapi.security import APIKeyHeader
from httpcore import request

from app.configs.database import get_db
from sqlalchemy.orm import Session
import logging

from app.services.auth_service import AuthService
from app.repository.auth_repo import AuthRepository
from app.schema.api_key_req import APIKeyReq
from app.schema.api_key_res import APIKeyRes

api_key_header = APIKeyHeader(name="x-api-key")

auth_router = APIRouter(prefix="/ricauth", tags=["ricauth"])
logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException, Depends, Header

@auth_router.post("/genAPIKey", response_model=APIKeyRes)
async def generateAppAPIKey(payload: APIKeyReq = None, db: Session = Depends(get_db)):
    
    client_id = payload.client_id if payload else None
    app_id = payload.app_id if payload else None
    client_secret = payload.client_secret if payload else None

    if client_id and app_id and client_secret:
        # validate the API key for the given app and client Id and then return the auth token (JWT)
        service = AuthService(AuthRepository(db))
        key_result = await service.generate_app_api_key(client_id, app_id, client_secret, 32)
        #print(f"After API Key Generation:  {key_result.key_hash}"  )
        result = APIKeyRes(
            client_id=key_result.client_id,
            app_id=key_result.app_id,
            key_id=key_result.key_id,
            key_hash=key_result.raw_key,  # Return the raw key to the client (not hashed) for initial display
            enabled=key_result.enabled
        )
        return result
    else:
        raise HTTPException(status_code=401, detail={"status": False, "error_code": 401, "error_desc": "Tenant ID, App ID and API Keys are mandory. Should be supplied as part of request header. One or all are missing."})
        

@auth_router.post("/GetAppAuthToken")
async def getAppAuthToken(request: Request = None, db: Session = Depends(get_db)):
    
    x_api_key = request.state.api_key
    x_tenant_id = request.state.tenant_id
    x_app_id = request.state.app_id

    if x_api_key and x_tenant_id and x_app_id:
        # validate the API key for the given app and client Id and then return the auth token (JWT)
        service = AuthService(AuthRepository(db))
        if hasattr(request.state, "auth_type") and request.state.auth_type == "api_key":
            #key = await service.validate_api_key(x_api_key)
            valid_key = await service.validate_api_key_by_client_app(x_api_key, x_tenant_id, x_app_id)

            auth_session = await service.generate_auth_token_by_client_app(x_tenant_id, x_app_id, "ricauth", valid_key.key_id, "system")

            result = {
                "success": True,
                "tenant_id": x_tenant_id,
                "app_id": x_app_id,
                "auth_key": auth_session.token if auth_session else None,
                "expires_at": auth_session.expires_at if auth_session else None     
            }

            print(f"After API Key Validation:  {result}")

            return result
    else:
        raise HTTPException(status_code=401, detail={"status": False, "error_code": 401, "error_desc": "Tenant ID, App ID and API Keys are mandory. Should be supplied as part of request header. One or all are missing."})
        

@auth_router.post("/TestAuthToken")
async def testAuthToken(request: Request = None, db: Session = Depends(get_db)):
    
    x_api_key = request.state.api_key
    x_tenant_id = request.state.tenant_id
    x_app_id = request.state.app_id

    if x_api_key and x_tenant_id and x_app_id:
        # validate the API key for the given app and client Id and then return the auth token (JWT)
        service = AuthService(AuthRepository(db))
        if hasattr(request.state, "auth_type") and request.state.auth_type == "jwt":
            #key = await service.validate_api_key(x_api_key)
            valid_key = await service.validate_api_key_by_client_app(x_api_key, x_tenant_id, x_app_id)

            auth_session = await service.validate_auth_token_by_client_app(x_tenant_id, x_app_id,request.state.token)

            result = {
                "success": True,
                "client_id": x_tenant_id,
                "app_id": x_app_id,
                "key_id": valid_key.key_id,
                "auth_key_token":request.state.token,
                "token_expiry": request.state.token_expiry
            }

            print(f"After API Key Validation:  {result}")

            return result
    else:
        raise HTTPException(status_code=401, detail={"status": False, "error_code": 401, "error_desc": "Tenant ID, App ID and API Keys are mandory. Should be supplied as part of request header. One or all are missing."})
        

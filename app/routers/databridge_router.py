from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse

from app.configs.database import get_db
from app.services.auth_service import AuthService
from app.repository.auth_repo import AuthRepository
from app.services.databridge_service import DataBridgeService
from app.repository.databridge_repo import DataBridgeRepo
from app.schema.cms_auto_close_req import CMSAutoCloseReq
from app.schema.reg_evidence_docs_dto import RegEvidenceDoc as RegEvidenceDocDTO

from sqlalchemy.orm import Session
import logging
from typing import List
import base64
import io

databridge_router = APIRouter(prefix="/databridge", tags=["databridge"])
logger = logging.getLogger(__name__)

@databridge_router.post("/GetDataForCMSAutoClosure")
async def getDataForCMSAutoClosure(request: Request=None, db: Session = Depends(get_db)):
    
    x_api_key = request.state.api_key
    x_tenant_id = request.state.tenant_id
    x_app_id = request.state.app_id

    if x_api_key and x_tenant_id and x_app_id:
        # validate the API key for the given app and client Id and then return the auth token (JWT)
        auth_service = AuthService(AuthRepository(db))
        if hasattr(request.state, "auth_type") and request.state.auth_type == "jwt":
            #key = await service.validate_api_key(x_api_key)
            valid_key = await auth_service.validate_api_key_by_client_app(x_api_key, x_tenant_id, x_app_id)

            auth_session = await auth_service.validate_auth_token_by_client_app(x_tenant_id, x_app_id,request.state.token)

            #DataBridge Service Calls
            databridge_service = DataBridgeService(DataBridgeRepo(db))

            #raw_body = await request.body()
            req_body = await request.json()
            req_body_data = req_body["data"]

            from pydantic import TypeAdapter
            adapter = TypeAdapter(List[CMSAutoCloseReq])
            cms_req = adapter.validate_python(req_body_data)

            print(f"CMS AutoClose Request Body Payload: {cms_req}")
            cms_auto_close_items = await databridge_service.getComplianceItemsForAutoClosure(x_tenant_id, x_app_id, cms_req)

            result = {
                        "success": True,
                        "status_code": 200,
                        "message": "Data fetched successfully",
                        "data": cms_auto_close_items
                    }

            #print(f"After API Key Validation:  {result}")

            return result
    else:
        raise HTTPException(status_code=401, detail={"status": False, "error_code": 401, "error_desc": "Tenant ID, App ID and API Keys are mandory. Should be supplied as part of request header. One or all are missing."})
        

@databridge_router.post("/SaveDocumentsForID")
async def saveDocumentsForID(request: Request, doc_id: str = Form(...), file_name: str = Form(...), file_type: str = Form(...), comments: str = Form(...), file_stream: UploadFile = File(...), db: Session = Depends(get_db)):
    
    x_api_key = request.state.api_key
    x_tenant_id = request.state.tenant_id
    x_app_id = request.state.app_id

    if x_api_key and x_tenant_id and x_app_id:
        # validate the API key for the given app and client Id and then return the auth token (JWT)
        auth_service = AuthService(AuthRepository(db))
        if hasattr(request.state, "auth_type") and request.state.auth_type == "jwt":
            #key = await service.validate_api_key(x_api_key)
            valid_key = await auth_service.validate_api_key_by_client_app(x_api_key, x_tenant_id, x_app_id)

            auth_session = await auth_service.validate_auth_token_by_client_app(x_tenant_id, x_app_id,request.state.token)

            #DataBridge Service Calls
            databridge_service = DataBridgeService(DataBridgeRepo(db))

            payload = {
                "doc_id": doc_id,
                "file_name": file_name,
                "file_type": file_type,
                "comments": comments
            }

            from pydantic import TypeAdapter
            adapter = TypeAdapter(RegEvidenceDocDTO)
            saveDocReq = adapter.validate_python(payload)

            print(f"Save Documents Body Payload: {saveDocReq} : File Content {file_stream}")

            compl_docs:RegEvidenceDocDTO = await databridge_service.saveDocumentsForID(x_tenant_id, x_app_id, saveDocReq, file_stream)

            if compl_docs:
                saved_compl_docs =  {
                                        "doc_id": compl_docs.doc_id,
                                        "file_name": compl_docs.file_name,
                                        "file_type": compl_docs.file_type,
                                        "comments": compl_docs.comments,
                                        "file_content": ""#compl_docs.file_stream
                                    }
            else:
                saved_compl_docs = {}

            result = {
                        "success": True,
                        "status_code": 200,
                        "message": "File uploaded successfully",
                        "data": saved_compl_docs
                    }

            #print(f"After API Key Validation:  {result}")

            return result
    else:
        raise HTTPException(status_code=401, detail={"status": False, "error_code": 401, "error_desc": "Tenant ID, App ID and API Keys are mandory. Should be supplied as part of request header. One or all are missing."})


@databridge_router.post("/GetDocumentsForID")
async def getDocumentsForID(request: Request = None, db: Session = Depends(get_db)):
    
    x_api_key = request.state.api_key
    x_tenant_id = request.state.tenant_id
    x_app_id = request.state.app_id

    if x_api_key and x_tenant_id and x_app_id:
        # validate the API key for the given app and client Id and then return the auth token (JWT)
        auth_service = AuthService(AuthRepository(db))
        if hasattr(request.state, "auth_type") and request.state.auth_type == "jwt":
            #key = await service.validate_api_key(x_api_key)
            valid_key = await auth_service.validate_api_key_by_client_app(x_api_key, x_tenant_id, x_app_id)

            auth_session = await auth_service.validate_auth_token_by_client_app(x_tenant_id, x_app_id,request.state.token)

            #DataBridge Service Calls
            databridge_service = DataBridgeService(DataBridgeRepo(db))

            #raw_body = await request.body()
            req_body = await request.json()
            req_body_data = req_body["data"]

            print(f"CMS AutoClose Request Body Payload: {req_body_data}")
            compDoc = await databridge_service.getDocumentsForID(x_tenant_id, x_app_id, req_body_data["DocumentID"], req_body_data["Clientname"], req_body_data["ClientURL"])

            if compDoc:
                compl_docs =  {
                                        "doc_id": compDoc.doc_id,
                                        "file_name": compDoc.file_name,
                                        "file_type": compDoc.file_type,
                                        "comments": compDoc.comments,
                                        "file_content": base64.b64encode(compDoc.file_stream).decode('ascii')
                                    }
            else:
                compl_docs = {}

            result = {
                        "success": True,
                        "status_code": 200,
                        "message": "Data fetched successfully",
                        "data": compl_docs
                    }

            #print(f"After API Key Validation:  {result}")

            #return result

            if compDoc and compDoc.file_stream:
                return StreamingResponse(
                    io.BytesIO(compDoc.file_stream),
                    media_type=compDoc.file_type,
                    headers={
                        "Content-Disposition": f"attachment; filename={compDoc.file_name}"
                    }
                )
            else:
                return {"success": False, "message": "Document not found for the given Document ID"}
    
    else:
        raise HTTPException(status_code=401, detail={"status": False, "error_code": 401, "error_desc": "Tenant ID, App ID and API Keys are mandory. Should be supplied as part of request header. One or all are missing."})


@databridge_router.post("/GetDataBridgeClientsFromCMS")
async def getDataBridgeClientsFromCMS(request: Request = None, db: Session = Depends(get_db)):
    
    x_api_key = request.state.api_key
    x_tenant_id = request.state.tenant_id
    x_app_id = request.state.app_id

    if x_api_key and x_tenant_id and x_app_id:
        # validate the API key for the given app and client Id and then return the auth token (JWT)
        auth_service = AuthService(AuthRepository(db))
        if hasattr(request.state, "auth_type") and request.state.auth_type == "jwt":
            #key = await service.validate_api_key(x_api_key)
            valid_key = await auth_service.validate_api_key_by_client_app(x_api_key, x_tenant_id, x_app_id)
            auth_session = await auth_service.validate_auth_token_by_client_app(x_tenant_id, x_app_id,request.state.token)

            #DataBridge Service Calls
            databridge_service = DataBridgeService(DataBridgeRepo(db))
            cms_clients = await databridge_service.getRegPortalCredentialsFromCMS()
            #print("####### Type of CMS Clients ######", type(cms_clients["data"]))  # should be dict

            upd_cms_clients = await databridge_service.saveRegPortalCredentialsFromCMS(x_tenant_id, x_app_id, cms_clients["data"])

            if upd_cms_clients:
                saved_cms_clients = [
                    item.model_dump(exclude={"id","created_at", "updated_at", "created_by", "updated_by"})
                    for item in upd_cms_clients
            ]
            else:
                saved_cms_clients = []

            """
            from app.utils.crypt_cms import CryptoCMS 
            import json

            first_user = saved_cms_clients[0]
            first_user_credentials = json.loads(first_user["credentials"])
            cred = first_user_credentials[0]
            decrypted_user = cred["UserName"]
            decrypted_pwd = cred["Password"]

            decrypted_user_name = CryptoCMS.action_dtbrdg_decrypt(decrypted_user)
            decrypted_user_pwd = CryptoCMS.action_dtbrdg_decrypt(decrypted_pwd)
            print(f"Decrypted User Name and Password : {decrypted_user_name} : {decrypted_user_pwd}")

            encrypted_user_name = CryptoCMS.action_dtbrdg_encrypt(decrypted_user_name)
            encrypted_user_pwd = CryptoCMS.action_dtbrdg_encrypt(decrypted_user_pwd)
            print(f"Encrypted User Name and Password: {encrypted_user_name} : {encrypted_user_pwd}")
            """
            result = {
                        "success": True,
                        "status_code": 200,
                        "message": "Data fetched successfully",
                        "data": saved_cms_clients
            }

            #print(f"After API Key Validation:  {result}")

            return result
    else:
        raise HTTPException(status_code=401, detail={"status": False, "error_code": 401, "error_desc": "Tenant ID, App ID and API Keys are mandory. Should be supplied as part of request header. One or all are missing."})

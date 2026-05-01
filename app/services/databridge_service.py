from app.configs.settings import settings
from app.repository.databridge_repo import DataBridgeRepo
from app.schema.cms_customers_dto import CMSCustomer as CMSCustomerDTO
from app.schema.reg_portal_evidences_dto import RegPortalEvidence as RegPortalEvidenceDTO
from app.schema.cms_auto_close_req import CMSAutoCloseReq
from app.schema.reg_evidence_docs_dto import RegEvidenceDoc as RegEvidenceDocDTO

from fastapi import HTTPException, UploadFile
import logging
import httpx
from typing import List
import json
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class DataBridgeService:
    def __init__(self, repo: DataBridgeRepo):
        self.repo = repo
        self.cms_api_url = settings.cms.cms_api_url
        self.cms_auth_token = settings.cms.cms_auth_token
        
    async def getRegPortalCredentialsFromCMS(self):
        headers = {
            "authtoken": self.cms_auth_token,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.cms_api_url + "/" + settings.cms.cms_clients_endpoint, headers=headers)

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"External API error: {response.text}"
                )

            data = response.json()
            #print(f"########### Tenant Clients: {data}")

            return data

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error calling external API: {str(e)}"
            )
    
    def mapCmsCustomersToDtBrdgCustomers(self, cms_customers: List, tenant_id: str, app_id: str, created_by: str = "", updated_by: str = "") -> List[CMSCustomerDTO]:
      """
      Convert API response data to a list of CMSCustomer DTOs.

      Args:
          api_data: The list from the "data" key of the API response.
          tenant_id: Tenant identifier (e.g., from current user context).
          app_id: Application identifier.
          created_by: Optional username or ID who created the records.
          updated_by: Optional username or ID who last updated the records.

      Returns:
          List of CMSCustomer objects.
      """
      customers = []
      now_str = datetime.now(timezone.utc)

      #print("TYPE:", type(cms_customers))
      #print("VALUE:", cms_customers)

      #print(f"############# CMS Customers: #############: {cms_customers}")
      for item in cms_customers:
          # Generate a new UUID for the id field
          record_id = str(uuid.uuid4())

          # Convert Credentials list to JSON string
          credentials_json = json.dumps(item.get("Credentials", []))

          # Convert CredentialManagers list to JSON string
          credential_managers_json = json.dumps(item.get("CredentialManagers", []))

          customer = CMSCustomerDTO(
              id=record_id,
              tenant_id=tenant_id,
              app_id=app_id,
              tenant_name=item.get("tenanat_name", ""),
              tenant_url=item.get("tenanat_url", ""),

              c_name=item.get("CName", ""),
              client_name=item.get("Clientname", ""),
              client_url=item.get("ClientUrl", ""),
              credentials=credentials_json,
              credential_managers=credential_managers_json,
              created_at=now_str,
              updated_at=now_str,
              created_by=created_by,
              updated_by=updated_by,
          )
          customers.append(customer)

      #print(f"############# Customers: #############: {customers}")
      return customers

    async def saveRegPortalCredentialsFromCMS(self, tenant_id, app_id, cms_clients: List):
        cms_clients = self.mapCmsCustomersToDtBrdgCustomers(cms_clients, tenant_id, app_id, "", "")

        save_cms_clients = await self.repo.saveCustomerCredentials(tenant_id, app_id, cms_clients)

        return cms_clients

    def mapCMSAutoCloseReqToDtBrdgActivities(self,tenant_id: str, app_id: str, compl_items_req: List[CMSAutoCloseReq])-> List[RegPortalEvidenceDTO]: 
        
        complianceItems = []

        for item in compl_items_req:
            complianceItem = RegPortalEvidenceDTO(
                tenant_id=tenant_id,
                app_id=app_id,
                #tenant_name=item.Clientname,
                tenant_name=item.CName,
                tenant_url=item.ClientURL,
                financial_year=str(item.FiscalYear),
                applicable_month=str(item.ApplicableMonth),
                ricago_section_id=str(item.RicagoSectionID)
            )
            complianceItems.append(complianceItem)
        
        return complianceItems

    def mapDtBrdgActivitiesToCMSAutoCloseResp(self, compliance_activities: List[RegPortalEvidenceDTO]) -> List[dict]:
        cms_auto_close_items = []

        for activity in compliance_activities:
            item = {
                "Clientname": activity.tenant_name,
                "FiscalYear": activity.financial_year,
                "ApplicableMonth": activity.applicable_month,
                "RicagoSectionId": activity.ricago_section_id,
                "UniqueIdentifierToConsider": activity.uid_to_consider,
                "OrgUniqueIdentifier": json.loads(activity.org_uid) if activity.org_uid else {"DisplayName":"","Value":""},
                "LocationUniqueIdentifier": json.loads(activity.loc_uid) if activity.loc_uid else {"DisplayName":"","Value":""},
                "ClosureDate": activity.closure_date,
                "DataBridgeDocID": activity.doc_id,
                "Comments": activity.comments
            }
            cms_auto_close_items.append(item)

        return cms_auto_close_items 

    async def getComplianceItemsForAutoClosure(self,tenant_id: str, app_id: str, compl_items_req: List[CMSAutoCloseReq]):

        complianceItemsForCMS = self.mapCMSAutoCloseReqToDtBrdgActivities(tenant_id, app_id, compl_items_req)
        
        complianceActivities = await self.repo.getComplianceItemsForAutoClosure(tenant_id, app_id, complianceItemsForCMS)
        
        cms_auto_close_items = self.mapDtBrdgActivitiesToCMSAutoCloseResp(complianceActivities)
        

        return cms_auto_close_items
    
    async def saveDocumentsForID(self, tenant_id: str, app_id: str, evidence: RegEvidenceDocDTO, file_stream: UploadFile)->RegEvidenceDocDTO:
        file_bytes = await file_stream.read()
        #evidence.file_stream = file_bytes
        saved_doc = await self.repo.saveDocumentsForID(tenant_id, app_id, evidence, file_bytes)
        #print(f"Saved document with ID: {saved_doc.id} for tenant_id: {tenant_id}, app_id: {app_id}")
        #print(f"######## works - service")
        return saved_doc

    async def getDocumentsForID(self, tenant_id: str, app_id: str, doc_id: str, c_name: str, tenant_url: str)-> RegEvidenceDocDTO:
        document = await self.repo.getDocumentsForID(tenant_id, app_id, doc_id,c_name, tenant_url)
        return document
    
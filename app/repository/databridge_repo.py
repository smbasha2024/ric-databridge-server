from app.schema.cms_customers_dto import CMSCustomer as CMSCustomerDTO
from app.models.cms_customers_model import CMSCustomer as CMSCustomerModel
from app.schema.reg_portal_evidences_dto import RegPortalEvidence as RegPortalEvidenceDTO
from app.models.reg_portal_evidences_model import RegPortalEvidence as RegPortalEvidenceModel

from app.schema.reg_evidence_docs_dto import RegEvidenceDoc as RegEvidenceDocDTO
from app.models.reg_evidence_docs_model import RegEvidenceDoc as RegEvidenceDocModel

from typing import Optional
from sqlalchemy import and_, select, desc
from datetime import datetime, timezone
from typing import List
import uuid

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------- Repository (DB calls) ---------------------- #
class DataBridgeRepo:
    """Handles all database interactions for authentication."""

    def __init__(self, db):
        self.db = db
    
    async def saveCustomerCredentials(self, tenant_id:str, app_id:str, cms_clients:List[CMSCustomerDTO], created_by: str = "",updated_by: str = ""):
        """
        Insert or update CMS customer credentials based on tenant_id and app_id.

        Args:
            tenant_id: Tenant identifier (used for lookup and assignment).
            app_id: Application identifier (used for lookup and assignment).
            cms_clients: List of CMSCustomer DTOs containing credential data.
            created_by: User who creates new records (default empty string).
            updated_by: User who updates records (default empty string).
        """
        now_str = datetime.now(timezone.utc)

        for client_dto in cms_clients:
            # Check if a record with the same tenant_id and app_id exists
            stmt = select(CMSCustomerModel).where(
                CMSCustomerModel.tenant_id == tenant_id,
                CMSCustomerModel.app_id == app_id,
                #CMSCustomerModel.tenant_url == client_dto.tenant_url
                CMSCustomerModel.c_name == client_dto.c_name
                #CMSCustomerModel.client_name == client_dto.client_name,
                #CMSCustomerModel.client_url == client_dto.client_url
            )
            result = self.db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # --- UPDATE existing record ---
                #existing.tenant_name = client_dto.tenant_name
                #existing.tenant_url = client_dto.tenant_url
                existing.c_name = client_dto.c_name,
                existing.client_name = client_dto.client_name,
                existing.client_url = client_dto.client_url,
                existing.credentials = client_dto.credentials
                existing.credential_managers = client_dto.credential_managers
                existing.updated_at = now_str
                existing.updated_by = updated_by
                # Do not change created_at / created_by
            else:
                # --- INSERT new record ---
                new_record = CMSCustomerModel(
                    id=uuid.uuid4(),
                    tenant_id=tenant_id,
                    app_id=app_id,
                    #tenant_url=client_dto.tenant_url,
                    c_name = client_dto.c_name,
                    client_name = client_dto.client_name,
                    client_url = client_dto.client_url,

                    credentials=client_dto.credentials,
                    credential_managers=client_dto.credential_managers,
                    created_at=now_str,
                    updated_at=now_str,
                    created_by=created_by,
                    updated_by=updated_by,
                )
                self.db.add(new_record)

        # Commit all changes after processing the list
        self.db.commit()

        return cms_clients
    
    async def getComplianceItemsForAutoClosure(self,tenant_id: str, app_id: str, activity_items: List[RegPortalEvidenceDTO]) -> List[RegPortalEvidenceDTO]:
        """
        For each input item, fetch matching records from reg_portal_evidences.

        Expected input dict keys:
            - Clientname (maps to tenant_id)
            - FiscalYear (maps to financial_year)
            - ApplicableMonth (maps to applicable_month)
            - RicagoSectionID (maps to ricago_section_id)

        Returns a flat list of all matching RegPortalEvidence records.
        """
        if not activity_items:
            return []

        # Build OR conditions: match any of the input combinations
        conditions = []
        for item in activity_items:
            cond = and_(
                RegPortalEvidenceModel.tenant_id == tenant_id,
                RegPortalEvidenceModel.app_id == app_id,
                #RegPortalEvidenceModel.tenant_name == item.tenant_name,
                RegPortalEvidenceModel.c_name == item.c_name,
                RegPortalEvidenceModel.financial_year == item.financial_year,
                RegPortalEvidenceModel.applicable_month == item.applicable_month,
                RegPortalEvidenceModel.ricago_section_id == item.ricago_section_id,
            )
            conditions.append(cond)

        # Combine with OR
        #stmt = select(RegPortalEvidenceModel).where(and_(False, *conditions))  # trick: OR via any
        # Simpler: use sqlalchemy.or_(*conditions)
        from sqlalchemy import or_
        #stmt = select(RegPortalEvidenceModel).where(or_(*conditions))

        stmt = select(RegPortalEvidenceModel).where(or_(*conditions))

        #print(f"SQL Statement to get the Compliances for Closure... {stmt}")

        # Log the compiled SQL (useful for debugging)
        compiled = stmt.compile(compile_kwargs={"literal_binds": True})
        logger.info(f"SQL Query: {compiled}")

        result = self.db.execute(stmt)
        rows = result.scalars().all()
        logger.info(f"Number of rows returned: {len(rows)}")
        
        return rows
    
    async def saveDocumentsForID(self, tenant_id: str, app_id: str, evidence: RegPortalEvidenceDTO, file_bytes):

        existing = self.db.execute(
        select(RegEvidenceDocModel).where(
            RegEvidenceDocModel.doc_id == evidence.doc_id,
            RegEvidenceDocModel.tenant_id == tenant_id,
            RegEvidenceDocModel.app_id == app_id
        )).scalar_one_or_none()

        #print(f"existing document for doc_id {existing.doc_id}, tenant_id {existing.tenant_id}, app_id {existing.app_id}")

        if existing:
            return existing
    
        saved_evidence = RegEvidenceDocModel(
            tenant_id=tenant_id,
            app_id=app_id,
            c_name=evidence.c_name,
            doc_id=evidence.doc_id,
            file_name=evidence.file_name,
            file_type=evidence.file_type,
            comments=evidence.comments,
            file_stream=file_bytes,

            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by="system",
            updated_by="system"
        )

        self.db.add(saved_evidence)
        self.db.commit()
        self.db.refresh(saved_evidence)
        #print(f"######## works - repo")
        return saved_evidence
    
    async def getDocumentsForID(self, tenant_id: str, app_id: str, doc_id: str, c_name: str, tenant_url: str):

        existing = self.db.execute(
        select(RegEvidenceDocModel).where(
            RegEvidenceDocModel.doc_id == doc_id,
            RegEvidenceDocModel.tenant_id == tenant_id,
            RegEvidenceDocModel.app_id == app_id,
            RegEvidenceDocModel.c_name == c_name
        )).scalar_one_or_none()

        #print(f"existing document for doc_id {existing.doc_id}, tenant_id {existing.tenant_id}, app_id {existing.app_id}")

        if existing:
            return existing
        else:
            return None
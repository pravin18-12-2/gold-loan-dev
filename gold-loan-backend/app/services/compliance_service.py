from fastapi import HTTPException
from app.repositories.compliance_repo import ComplianceRepository

class ComplianceService:
    def __init__(self):
        self.repo = ComplianceRepository()

    def create(self, db, tenant_id, loan_id, payload):
        if len(payload['jewel_images']) != payload['total_jewel_count']:
            raise HTTPException(status_code=400, detail='jewel_images count must match total_jewel_count')
        return self.repo.create(db, tenant_id, loan_id, payload)

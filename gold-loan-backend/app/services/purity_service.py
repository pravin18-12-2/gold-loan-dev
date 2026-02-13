import uuid
from app.repositories.purity_repo import PurityRepository

class PurityService:
    def __init__(self):
        self.repo = PurityRepository()

    def trigger(self, db, tenant_id, loan_id):
        self.repo.upsert_default(db, tenant_id, loan_id)
        return {'job_id': str(uuid.uuid4()), 'status': 'PROCESSING'}

    def list(self, db, tenant_id, loan_id):
        return self.repo.list_by_loan(db, tenant_id, loan_id)

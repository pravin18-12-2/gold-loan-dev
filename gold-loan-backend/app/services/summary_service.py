import json
from app.repositories.summary_repo import SummaryRepository

class SummaryService:
    def __init__(self):
        self.repo = SummaryRepository()

    def generate(self, db, tenant_id, loan):
        row = self.repo.get_by_loan(db, tenant_id, loan.id)
        if row:
            return row
        snapshot = json.dumps({
            'loan_id': loan.id,
            'status': loan.status,
            'customer_id': loan.customer_id,
            'appraiser_id': loan.appraiser_id,
        })
        return self.repo.create(db, tenant_id, loan.id, snapshot)

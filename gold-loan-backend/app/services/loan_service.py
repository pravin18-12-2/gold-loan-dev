from datetime import datetime, timezone
from fastapi import HTTPException
from app.repositories.loan_repo import LoanRepository

class LoanService:
    def __init__(self):
        self.repo = LoanRepository()

    def create(self, db, tenant_id, payload):
        return self.repo.create(db, tenant_id, payload)

    def get(self, db, tenant_id, loan_id):
        loan = self.repo.get(db, tenant_id, loan_id)
        if not loan:
            raise HTTPException(status_code=404, detail='Loan not found')
        return loan

    def ensure_open(self, loan):
        if loan.status == 'COMPLETED':
            raise HTTPException(status_code=403, detail='Loan already completed')

    def complete(self, db, loan):
        if loan.status != 'COMPLETED':
            loan.status = 'COMPLETED'
            loan.completed_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(loan)
        return loan

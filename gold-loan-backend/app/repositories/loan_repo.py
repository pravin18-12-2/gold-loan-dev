from sqlalchemy.orm import Session
from app.models.loan import Loan

class LoanRepository:
    def create(self, db: Session, tenant_id: str, payload: dict) -> Loan:
        rec = Loan(tenant_id=tenant_id, **payload)
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec

    def get(self, db: Session, tenant_id: str, loan_id: str):
        return db.query(Loan).filter_by(tenant_id=tenant_id, id=loan_id).first()

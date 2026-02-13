from sqlalchemy.orm import Session
from app.models.summary import LoanSummary

class SummaryRepository:
    def get_by_loan(self, db: Session, tenant_id: str, loan_id: str):
        return db.query(LoanSummary).filter_by(tenant_id=tenant_id, loan_id=loan_id).first()

    def create(self, db: Session, tenant_id: str, loan_id: str, snapshot_json: str):
        rec = LoanSummary(tenant_id=tenant_id, loan_id=loan_id, snapshot_json=snapshot_json)
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec

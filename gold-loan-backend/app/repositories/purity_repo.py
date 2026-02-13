from sqlalchemy.orm import Session
from app.models.purity import PurityTest

class PurityRepository:
    def upsert_default(self, db: Session, tenant_id: str, loan_id: str):
        row = db.query(PurityTest).filter_by(tenant_id=tenant_id, loan_id=loan_id).first()
        if row:
            return row
        row = PurityTest(tenant_id=tenant_id, loan_id=loan_id, jewel_index=1, result='PASS', confidence_score=0.92)
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    def list_by_loan(self, db: Session, tenant_id: str, loan_id: str):
        return db.query(PurityTest).filter_by(tenant_id=tenant_id, loan_id=loan_id).all()

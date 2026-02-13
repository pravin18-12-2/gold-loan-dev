from sqlalchemy.orm import Session
from app.models.appraiser import Appraiser

class AppraiserRepository:
    def create(self, db: Session, tenant_id: str, payload: dict) -> Appraiser:
        rec = Appraiser(tenant_id=tenant_id, **payload)
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec

    def list(self, db: Session, tenant_id: str):
        return db.query(Appraiser).filter_by(tenant_id=tenant_id).all()

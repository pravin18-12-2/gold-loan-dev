from sqlalchemy.orm import Session
from app.models.customer import Customer

class CustomerRepository:
    def create(self, db: Session, tenant_id: str, payload: dict) -> Customer:
        rec = Customer(tenant_id=tenant_id, **payload)
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec

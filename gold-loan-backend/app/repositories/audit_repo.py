import json
from sqlalchemy.orm import Session
from app.models.audit import AuditLog

class AuditRepository:
    def write(self, db: Session, tenant_id: str, action: str, entity_type: str, entity_id: str, metadata: dict | None = None):
        db.add(AuditLog(tenant_id=tenant_id, action=action, entity_type=entity_type, entity_id=entity_id, metadata=json.dumps(metadata or {})))
        db.commit()

    def list(self, db: Session, tenant_id: str, entity_type: str, entity_id: str):
        return db.query(AuditLog).filter_by(tenant_id=tenant_id, entity_type=entity_type, entity_id=entity_id).all()

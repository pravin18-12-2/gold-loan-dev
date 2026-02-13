import json
from app.repositories.audit_repo import AuditRepository

class AuditService:
    def __init__(self):
        self.repo = AuditRepository()

    def log(self, db, tenant_id, action, entity_type, entity_id, metadata=None):
        self.repo.write(db, tenant_id, action, entity_type, entity_id, metadata)

    def list(self, db, tenant_id, entity_type, entity_id):
        rows = self.repo.list(db, tenant_id, entity_type, entity_id)
        return [
            {
                'id': r.id,
                'action': r.action,
                'entity_type': r.entity_type,
                'entity_id': r.entity_id,
                'metadata': json.loads(r.metadata),
                'created_at': r.created_at.isoformat(),
            }
            for r in rows
        ]

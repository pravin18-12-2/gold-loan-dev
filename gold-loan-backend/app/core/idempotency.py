import hashlib
import json
from sqlalchemy.orm import Session
from app.models.idempotency import IdempotencyRecord


def _hash(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def get_cached(db: Session, tenant_id: str, key: str, endpoint: str, payload: dict):
    row = db.query(IdempotencyRecord).filter_by(tenant_id=tenant_id, key=key, endpoint=endpoint).first()
    if not row:
        return None
    if row.request_hash != _hash(payload):
        raise ValueError('Idempotency-Key reused with different payload')
    return json.loads(row.response_payload)


def store_response(db: Session, tenant_id: str, key: str, endpoint: str, payload: dict, response: dict):
    row = IdempotencyRecord(
        tenant_id=tenant_id,
        key=key,
        endpoint=endpoint,
        request_hash=_hash(payload),
        response_payload=json.dumps(response),
    )
    db.add(row)
    db.commit()

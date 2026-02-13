from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.config.security import auth_headers
from app.core.database import get_db
from app.core.exceptions import success
from app.core.idempotency import get_cached, store_response
from app.schemas.appraiser_schema import CreateAppraiserRequest
from app.services.appraiser_service import AppraiserService
from app.services.audit_service import AuditService

router = APIRouter(prefix='/appraisers', tags=['Appraisers'])
service = AppraiserService()
audit = AuditService()

@router.post('')
def create(payload: CreateAppraiserRequest, ctx: dict = Depends(auth_headers), db: Session = Depends(get_db), idempotency_key: str = Header(..., alias='Idempotency-Key')):
    endpoint = '/appraisers'
    body = payload.model_dump()
    try:
        cached = get_cached(db, ctx['tenant_id'], idempotency_key, endpoint, body)
    except ValueError as ex:
        raise HTTPException(status_code=409, detail=str(ex))
    if cached:
        return cached
    rec = service.create(db, ctx['tenant_id'], body)
    audit.log(db, ctx['tenant_id'], 'CREATE_APPRAISER', 'APPRAISER', rec.id)
    resp = success({'appraiser_id': rec.id, 'status': rec.status})
    store_response(db, ctx['tenant_id'], idempotency_key, endpoint, body, resp)
    return resp

@router.get('')
def list_appraisers(ctx: dict = Depends(auth_headers), db: Session = Depends(get_db)):
    rows = service.list(db, ctx['tenant_id'])
    return success([{'id': r.id, 'name': r.name, 'branch_id': r.branch_id, 'status': r.status} for r in rows])

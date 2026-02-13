from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.config.security import auth_headers
from app.core.database import get_db
from app.core.exceptions import success
from app.core.idempotency import get_cached, store_response
from app.schemas.compliance_schema import ComplianceRequest
from app.services.compliance_service import ComplianceService
from app.services.loan_service import LoanService

router = APIRouter(prefix='/loans', tags=['Compliance'])
service = ComplianceService()
loan_service = LoanService()

@router.post('/{loan_id}/compliance')
def create(loan_id: str, payload: ComplianceRequest, ctx: dict = Depends(auth_headers), db: Session = Depends(get_db), idempotency_key: str = Header(..., alias='Idempotency-Key')):
    endpoint = '/loans/{loan_id}/compliance'
    body = payload.model_dump() | {'loan_id': loan_id}
    try:
        cached = get_cached(db, ctx['tenant_id'], idempotency_key, endpoint, body)
    except ValueError as ex:
        raise HTTPException(status_code=409, detail=str(ex))
    if cached:
        return cached
    loan = loan_service.get(db, ctx['tenant_id'], loan_id)
    loan_service.ensure_open(loan)
    service.create(db, ctx['tenant_id'], loan_id, payload.model_dump())
    loan.status = 'COMPLIANCE_CAPTURED'
    db.commit()
    resp = success({'status': 'COMPLIANCE_CAPTURED'})
    store_response(db, ctx['tenant_id'], idempotency_key, endpoint, body, resp)
    return resp

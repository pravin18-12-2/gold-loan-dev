from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.config.security import auth_headers
from app.core.database import get_db
from app.core.exceptions import success
from app.core.idempotency import get_cached, store_response
from app.schemas.loan_schema import CreateLoanRequest
from app.services.loan_service import LoanService
from app.services.audit_service import AuditService

router = APIRouter(prefix='/loans', tags=['Loans'])
service = LoanService()
audit = AuditService()

@router.post('')
def create(payload: CreateLoanRequest, ctx: dict = Depends(auth_headers), db: Session = Depends(get_db), idempotency_key: str = Header(..., alias='Idempotency-Key')):
    endpoint = '/loans'
    body = payload.model_dump()
    try:
        cached = get_cached(db, ctx['tenant_id'], idempotency_key, endpoint, body)
    except ValueError as ex:
        raise HTTPException(status_code=409, detail=str(ex))
    if cached:
        return cached
    rec = service.create(db, ctx['tenant_id'], body)
    audit.log(db, ctx['tenant_id'], 'CREATE_LOAN', 'LOAN', rec.id)
    resp = success({'loan_id': rec.id, 'status': rec.status})
    store_response(db, ctx['tenant_id'], idempotency_key, endpoint, body, resp)
    return resp

@router.get('/{loan_id}')
def get_loan(loan_id: str, ctx: dict = Depends(auth_headers), db: Session = Depends(get_db)):
    loan = service.get(db, ctx['tenant_id'], loan_id)
    return success({'loan_id': loan.id, 'status': loan.status, 'customer_id': loan.customer_id})

@router.post('/{loan_id}/complete')
def complete(loan_id: str, ctx: dict = Depends(auth_headers), db: Session = Depends(get_db), idempotency_key: str = Header(..., alias='Idempotency-Key')):
    endpoint = '/loans/{loan_id}/complete'
    body = {'loan_id': loan_id}
    try:
        cached = get_cached(db, ctx['tenant_id'], idempotency_key, endpoint, body)
    except ValueError as ex:
        raise HTTPException(status_code=409, detail=str(ex))
    if cached:
        return cached
    loan = service.get(db, ctx['tenant_id'], loan_id)
    loan = service.complete(db, loan)
    audit.log(db, ctx['tenant_id'], 'COMPLETE_LOAN', 'LOAN', loan_id)
    resp = success({'status': 'COMPLETED', 'completed_at': loan.completed_at.isoformat()})
    store_response(db, ctx['tenant_id'], idempotency_key, endpoint, body, resp)
    return resp

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.config.security import auth_headers
from app.core.database import get_db
from app.core.exceptions import success
from app.core.idempotency import get_cached, store_response
from app.services.loan_service import LoanService
from app.services.purity_service import PurityService

router = APIRouter(prefix='/loans', tags=['Purity'])
loan_service = LoanService()
service = PurityService()

@router.post('/{loan_id}/purity-test')
def trigger(loan_id: str, ctx: dict = Depends(auth_headers), db: Session = Depends(get_db), idempotency_key: str = Header(..., alias='Idempotency-Key')):
    endpoint = '/loans/{loan_id}/purity-test'
    body = {'loan_id': loan_id}
    try:
        cached = get_cached(db, ctx['tenant_id'], idempotency_key, endpoint, body)
    except ValueError as ex:
        raise HTTPException(status_code=409, detail=str(ex))
    if cached:
        return cached
    loan = loan_service.get(db, ctx['tenant_id'], loan_id)
    loan_service.ensure_open(loan)
    result = service.trigger(db, ctx['tenant_id'], loan_id)
    loan.status = 'PURITY_TESTED'
    db.commit()
    resp = success(result)
    store_response(db, ctx['tenant_id'], idempotency_key, endpoint, body, resp)
    return resp

@router.get('/{loan_id}/purity-test')
def list_purity(loan_id: str, ctx: dict = Depends(auth_headers), db: Session = Depends(get_db)):
    rows = service.list(db, ctx['tenant_id'], loan_id)
    return success([{'jewel_index': r.jewel_index, 'result': r.result, 'confidence': r.confidence_score} for r in rows])

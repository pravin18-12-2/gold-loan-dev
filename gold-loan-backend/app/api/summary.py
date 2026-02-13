from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.config.security import auth_headers
from app.core.database import get_db
from app.core.exceptions import success
from app.core.idempotency import get_cached, store_response
from app.services.loan_service import LoanService
from app.services.summary_service import SummaryService

router = APIRouter(prefix='/loans', tags=['Summary'])
loan_service = LoanService()
service = SummaryService()

@router.post('/{loan_id}/summary')
def generate(loan_id: str, ctx: dict = Depends(auth_headers), db: Session = Depends(get_db), idempotency_key: str = Header(..., alias='Idempotency-Key')):
    endpoint = '/loans/{loan_id}/summary'
    body = {'loan_id': loan_id}
    try:
        cached = get_cached(db, ctx['tenant_id'], idempotency_key, endpoint, body)
    except ValueError as ex:
        raise HTTPException(status_code=409, detail=str(ex))
    if cached:
        return cached
    loan = loan_service.get(db, ctx['tenant_id'], loan_id)
    row = service.generate(db, ctx['tenant_id'], loan)
    resp = success({'summary_id': row.id})
    store_response(db, ctx['tenant_id'], idempotency_key, endpoint, body, resp)
    return resp

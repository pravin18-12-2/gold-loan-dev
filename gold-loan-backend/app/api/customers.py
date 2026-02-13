from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.config.security import auth_headers
from app.core.database import get_db
from app.core.exceptions import success
from app.core.idempotency import get_cached, store_response
from app.schemas.customer_schema import CreateCustomerRequest
from app.services.customer_service import CustomerService

router = APIRouter(prefix='/customers', tags=['Customers'])
service = CustomerService()

@router.post('')
def create(payload: CreateCustomerRequest, ctx: dict = Depends(auth_headers), db: Session = Depends(get_db), idempotency_key: str = Header(..., alias='Idempotency-Key')):
    endpoint = '/customers'
    body = payload.model_dump()
    try:
        cached = get_cached(db, ctx['tenant_id'], idempotency_key, endpoint, body)
    except ValueError as ex:
        raise HTTPException(status_code=409, detail=str(ex))
    if cached:
        return cached
    rec = service.create(db, ctx['tenant_id'], body)
    resp = success({'customer_id': rec.id})
    store_response(db, ctx['tenant_id'], idempotency_key, endpoint, body, resp)
    return resp

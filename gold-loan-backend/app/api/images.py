from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.config.security import auth_headers
from app.core.database import get_db
from app.core.exceptions import success
from app.core.idempotency import get_cached, store_response
from app.schemas.image_schema import UploadUrlRequest
from app.services.image_service import ImageService

router = APIRouter(prefix='/images', tags=['Images'])
service = ImageService()

@router.post('/upload-url')
def upload_url(payload: UploadUrlRequest, ctx: dict = Depends(auth_headers), db: Session = Depends(get_db), idempotency_key: str = Header(..., alias='Idempotency-Key')):
    endpoint = '/images/upload-url'
    body = payload.model_dump()
    try:
        cached = get_cached(db, ctx['tenant_id'], idempotency_key, endpoint, body)
    except ValueError as ex:
        raise HTTPException(status_code=409, detail=str(ex))
    if cached:
        return cached
    resp = success(service.upload_url())
    store_response(db, ctx['tenant_id'], idempotency_key, endpoint, body, resp)
    return resp

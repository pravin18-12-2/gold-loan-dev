from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.config.security import auth_headers
from app.core.database import get_db
from app.core.idempotency import get_cached, store_response
from app.core.exceptions import success
from app.schemas.auth_schema import LoginRequest, FaceVerifyRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix='/auth', tags=['Auth'])
service = AuthService()

@router.post('/login')
def login(payload: LoginRequest):
    return success(service.login())

@router.post('/face-verify')
def face_verify(
    payload: FaceVerifyRequest,
    ctx: dict = Depends(auth_headers),
    db: Session = Depends(get_db),
    idempotency_key: str = Header(..., alias='Idempotency-Key'),
):
    endpoint = '/auth/face-verify'
    body = payload.model_dump()
    try:
        cached = get_cached(db, ctx['tenant_id'], idempotency_key, endpoint, body)
    except ValueError as ex:
        raise HTTPException(status_code=409, detail=str(ex))
    if cached:
        return cached
    resp = success(service.face_verify())
    store_response(db, ctx['tenant_id'], idempotency_key, endpoint, body, resp)
    return resp

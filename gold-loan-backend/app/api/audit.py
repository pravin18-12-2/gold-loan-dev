from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.security import auth_headers
from app.core.database import get_db
from app.core.exceptions import success
from app.services.audit_service import AuditService

router = APIRouter(prefix='/audit', tags=['Audit'])
service = AuditService()

@router.get('')
def get_logs(entity_type: str, entity_id: str, ctx: dict = Depends(auth_headers), db: Session = Depends(get_db)):
    return success(service.list(db, ctx['tenant_id'], entity_type, entity_id))

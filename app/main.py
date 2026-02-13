import hashlib
import json
import uuid
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import (
    Appraiser,
    AuditLog,
    Customer,
    IdempotencyRecord,
    Loan,
    LoanSummary,
    PurityTest,
    RbiCompliance,
    RbiComplianceItem,
)
from app.schemas import (
    ComplianceRequest,
    CreateAppraiserRequest,
    CreateCustomerRequest,
    CreateLoanRequest,
    FaceVerifyRequest,
    LoginRequest,
    UploadUrlRequest,
)

app = FastAPI(title="Gold Loan Backend", version="v1")
Base.metadata.create_all(bind=engine)

CRITICAL_POSTS = {
    "/auth/face-verify",
    "/appraisers",
    "/customers",
    "/loans",
    "/loans/{loan_id}/compliance",
    "/loans/{loan_id}/purity-test",
    "/loans/{loan_id}/summary",
    "/loans/{loan_id}/complete",
    "/images/upload-url",
}


def meta(request_id: str):
    return {
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "v1",
    }


def ok(data, request_id: str):
    return {"success": True, "data": data, "meta": meta(request_id)}


def audit(db: Session, tenant_id: str, action: str, entity_type: str, entity_id: str, metadata: dict | None = None):
    rec = AuditLog(
        tenant_id=tenant_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata=json.dumps(metadata or {}),
    )
    db.add(rec)
    db.commit()


def auth_guard(authorization: str = Header(...), x_tenant_id: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID is required")
    return x_tenant_id


def idempotency_lookup(
    db: Session,
    tenant_id: str,
    endpoint: str,
    idem_key: str,
    body: dict,
):
    body_hash = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    existing = (
        db.query(IdempotencyRecord)
        .filter(
            IdempotencyRecord.tenant_id == tenant_id,
            IdempotencyRecord.key == idem_key,
            IdempotencyRecord.endpoint == endpoint,
        )
        .first()
    )
    if existing:
        if existing.request_hash != body_hash:
            raise HTTPException(status_code=409, detail="Idempotency key reused with different payload")
        return json.loads(existing.response_payload)
    return None


def idempotency_store(db: Session, tenant_id: str, endpoint: str, idem_key: str, body: dict, response: dict):
    body_hash = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    rec = IdempotencyRecord(
        tenant_id=tenant_id,
        key=idem_key,
        endpoint=endpoint,
        request_hash=body_hash,
        response_payload=json.dumps(response),
    )
    db.add(rec)
    db.commit()


def must_be_open_loan(loan: Loan):
    if loan.status == "COMPLETED":
        raise HTTPException(status_code=403, detail="Loan already completed")


@app.exception_handler(HTTPException)
async def http_exc(_: Request, exc: HTTPException):
    request_id = str(uuid.uuid4())
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {"code": "HTTP_ERROR", "message": str(exc.detail)},
            "meta": meta(request_id),
        },
    )


@app.post("/api/v1/auth/login")
def login(payload: LoginRequest):
    request_id = str(uuid.uuid4())
    return ok(
        {
            "access_token": f"token-{uuid.uuid4()}",
            "refresh_token": f"refresh-{uuid.uuid4()}",
            "role": "APPRAISER",
            "expires_in": 3600,
        },
        request_id,
    )


@app.post("/api/v1/auth/face-verify")
def face_verify(
    payload: FaceVerifyRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    tenant_id: str = Depends(auth_guard),
    db: Session = Depends(get_db),
):
    request_id = str(uuid.uuid4())
    endpoint = "/auth/face-verify"
    cached = idempotency_lookup(db, tenant_id, endpoint, idempotency_key, payload.model_dump())
    if cached:
        return cached
    response = ok({"verified": True, "confidence": 0.94}, request_id)
    idempotency_store(db, tenant_id, endpoint, idempotency_key, payload.model_dump(), response)
    return response


@app.post("/api/v1/appraisers", status_code=201)
def create_appraiser(
    payload: CreateAppraiserRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    tenant_id: str = Depends(auth_guard),
    db: Session = Depends(get_db),
):
    request_id = str(uuid.uuid4())
    endpoint = "/appraisers"
    body = payload.model_dump()
    cached = idempotency_lookup(db, tenant_id, endpoint, idempotency_key, body)
    if cached:
        return cached

    rec = Appraiser(tenant_id=tenant_id, **body)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    audit(db, tenant_id, "CREATE_APPRAISER", "APPRAISER", rec.id)
    response = ok({"appraiser_id": rec.id, "status": rec.status}, request_id)
    idempotency_store(db, tenant_id, endpoint, idempotency_key, body, response)
    return response


@app.get("/api/v1/appraisers")
def list_appraisers(tenant_id: str = Depends(auth_guard), db: Session = Depends(get_db)):
    request_id = str(uuid.uuid4())
    rows = db.query(Appraiser).filter(Appraiser.tenant_id == tenant_id).all()
    return ok(
        [
            {"id": r.id, "name": r.name, "branch_id": r.branch_id, "status": r.status}
            for r in rows
        ],
        request_id,
    )


@app.post("/api/v1/customers", status_code=201)
def create_customer(
    payload: CreateCustomerRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    tenant_id: str = Depends(auth_guard),
    db: Session = Depends(get_db),
):
    request_id = str(uuid.uuid4())
    endpoint = "/customers"
    body = payload.model_dump()
    cached = idempotency_lookup(db, tenant_id, endpoint, idempotency_key, body)
    if cached:
        return cached
    rec = Customer(tenant_id=tenant_id, **body)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    audit(db, tenant_id, "CREATE_CUSTOMER", "CUSTOMER", rec.id)
    response = ok({"customer_id": rec.id}, request_id)
    idempotency_store(db, tenant_id, endpoint, idempotency_key, body, response)
    return response


@app.post("/api/v1/loans", status_code=201)
def create_loan(
    payload: CreateLoanRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    tenant_id: str = Depends(auth_guard),
    db: Session = Depends(get_db),
):
    request_id = str(uuid.uuid4())
    endpoint = "/loans"
    body = payload.model_dump()
    cached = idempotency_lookup(db, tenant_id, endpoint, idempotency_key, body)
    if cached:
        return cached
    rec = Loan(tenant_id=tenant_id, **body)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    audit(db, tenant_id, "CREATE_LOAN", "LOAN", rec.id)
    response = ok({"loan_id": rec.id, "status": rec.status}, request_id)
    idempotency_store(db, tenant_id, endpoint, idempotency_key, body, response)
    return response


@app.get("/api/v1/loans/{loan_id}")
def get_loan(loan_id: str, tenant_id: str = Depends(auth_guard), db: Session = Depends(get_db)):
    request_id = str(uuid.uuid4())
    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.tenant_id == tenant_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return ok({"loan_id": loan.id, "status": loan.status, "customer_id": loan.customer_id}, request_id)


@app.post("/api/v1/loans/{loan_id}/compliance")
def create_compliance(
    loan_id: str,
    payload: ComplianceRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    tenant_id: str = Depends(auth_guard),
    db: Session = Depends(get_db),
):
    request_id = str(uuid.uuid4())
    endpoint = "/loans/{loan_id}/compliance"
    body = payload.model_dump()
    cached = idempotency_lookup(db, tenant_id, endpoint, idempotency_key, body | {"loan_id": loan_id})
    if cached:
        return cached

    if len(payload.jewel_images) != payload.total_jewel_count:
        raise HTTPException(status_code=400, detail="jewel_images count must match total_jewel_count")

    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.tenant_id == tenant_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    must_be_open_loan(loan)

    rec = RbiCompliance(
        tenant_id=tenant_id,
        loan_id=loan_id,
        total_jewel_count=payload.total_jewel_count,
        overall_image_id=payload.overall_image_id,
    )
    db.add(rec)
    db.flush()
    for item in payload.jewel_images:
        db.add(
            RbiComplianceItem(
                tenant_id=tenant_id,
                compliance_id=rec.id,
                jewel_index=item.index,
                jewel_image_id=item.image_id,
            )
        )
    loan.status = "COMPLIANCE_CAPTURED"
    db.commit()
    audit(db, tenant_id, "CAPTURE_COMPLIANCE", "LOAN", loan_id)
    response = ok({"status": "COMPLIANCE_CAPTURED"}, request_id)
    idempotency_store(db, tenant_id, endpoint, idempotency_key, body | {"loan_id": loan_id}, response)
    return response


@app.post("/api/v1/loans/{loan_id}/purity-test")
def trigger_purity(
    loan_id: str,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    tenant_id: str = Depends(auth_guard),
    db: Session = Depends(get_db),
):
    request_id = str(uuid.uuid4())
    endpoint = "/loans/{loan_id}/purity-test"
    body = {"loan_id": loan_id}
    cached = idempotency_lookup(db, tenant_id, endpoint, idempotency_key, body)
    if cached:
        return cached

    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.tenant_id == tenant_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    must_be_open_loan(loan)

    if not db.query(PurityTest).filter(PurityTest.loan_id == loan_id, PurityTest.tenant_id == tenant_id).first():
        db.add(PurityTest(tenant_id=tenant_id, loan_id=loan_id, jewel_index=1, result="PASS", confidence_score=0.92))
        loan.status = "PURITY_TESTED"
        db.commit()
    job_id = str(uuid.uuid4())
    audit(db, tenant_id, "TRIGGER_PURITY_TEST", "LOAN", loan_id, {"job_id": job_id})
    response = ok({"job_id": job_id, "status": "PROCESSING"}, request_id)
    idempotency_store(db, tenant_id, endpoint, idempotency_key, body, response)
    return response


@app.get("/api/v1/loans/{loan_id}/purity-test")
def get_purity(loan_id: str, tenant_id: str = Depends(auth_guard), db: Session = Depends(get_db)):
    request_id = str(uuid.uuid4())
    rows = db.query(PurityTest).filter(PurityTest.loan_id == loan_id, PurityTest.tenant_id == tenant_id).all()
    return ok(
        [
            {"jewel_index": r.jewel_index, "result": r.result, "confidence": r.confidence_score}
            for r in rows
        ],
        request_id,
    )


@app.post("/api/v1/images/upload-url")
def upload_url(
    payload: UploadUrlRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    tenant_id: str = Depends(auth_guard),
    db: Session = Depends(get_db),
):
    request_id = str(uuid.uuid4())
    endpoint = "/images/upload-url"
    body = payload.model_dump()
    cached = idempotency_lookup(db, tenant_id, endpoint, idempotency_key, body)
    if cached:
        return cached
    image_id = str(uuid.uuid4())
    response = ok({"image_id": image_id, "upload_url": f"https://s3-presigned/{image_id}"}, request_id)
    idempotency_store(db, tenant_id, endpoint, idempotency_key, body, response)
    return response


@app.post("/api/v1/loans/{loan_id}/summary")
def summary(
    loan_id: str,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    tenant_id: str = Depends(auth_guard),
    db: Session = Depends(get_db),
):
    request_id = str(uuid.uuid4())
    endpoint = "/loans/{loan_id}/summary"
    body = {"loan_id": loan_id}
    cached = idempotency_lookup(db, tenant_id, endpoint, idempotency_key, body)
    if cached:
        return cached

    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.tenant_id == tenant_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    existing = db.query(LoanSummary).filter(LoanSummary.loan_id == loan_id, LoanSummary.tenant_id == tenant_id).first()
    if existing:
        response = ok({"summary_id": existing.id}, request_id)
    else:
        snapshot = {
            "loan_id": loan.id,
            "status": loan.status,
            "customer_id": loan.customer_id,
            "appraiser_id": loan.appraiser_id,
        }
        rec = LoanSummary(tenant_id=tenant_id, loan_id=loan_id, snapshot_json=json.dumps(snapshot))
        db.add(rec)
        db.commit()
        db.refresh(rec)
        audit(db, tenant_id, "GENERATE_SUMMARY", "LOAN", loan_id, {"summary_id": rec.id})
        response = ok({"summary_id": rec.id}, request_id)

    idempotency_store(db, tenant_id, endpoint, idempotency_key, body, response)
    return response


@app.post("/api/v1/loans/{loan_id}/complete")
def complete_loan(
    loan_id: str,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    tenant_id: str = Depends(auth_guard),
    db: Session = Depends(get_db),
):
    request_id = str(uuid.uuid4())
    endpoint = "/loans/{loan_id}/complete"
    body = {"loan_id": loan_id}
    cached = idempotency_lookup(db, tenant_id, endpoint, idempotency_key, body)
    if cached:
        return cached

    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.tenant_id == tenant_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.status != "COMPLETED":
        loan.status = "COMPLETED"
        loan.completed_at = datetime.now(timezone.utc)
        db.commit()
    audit(db, tenant_id, "COMPLETE_LOAN", "LOAN", loan_id)
    response = ok({"status": "COMPLETED", "completed_at": loan.completed_at.isoformat()}, request_id)
    idempotency_store(db, tenant_id, endpoint, idempotency_key, body, response)
    return response


@app.get("/api/v1/audit")
def get_audit(entity_type: str, entity_id: str, tenant_id: str = Depends(auth_guard), db: Session = Depends(get_db)):
    request_id = str(uuid.uuid4())
    rows = (
        db.query(AuditLog)
        .filter(
            AuditLog.tenant_id == tenant_id,
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id,
        )
        .all()
    )
    return ok(
        [
            {
                "id": r.id,
                "action": r.action,
                "entity_type": r.entity_type,
                "entity_id": r.entity_id,
                "metadata": json.loads(r.metadata),
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ],
        request_id,
    )

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class Appraiser(Base):
    __tablename__ = "appraiser"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    branch_id: Mapped[str] = mapped_column(String)
    appraiser_code: Mapped[str] = mapped_column(String, unique=True)
    face_image_id: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Customer(Base):
    __tablename__ = "customer"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    customer_code: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    face_image_id: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Loan(Base):
    __tablename__ = "loan"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    customer_id: Mapped[str] = mapped_column(String, ForeignKey("customer.id"))
    appraiser_id: Mapped[str] = mapped_column(String, ForeignKey("appraiser.id"))
    bank_id: Mapped[str] = mapped_column(String)
    branch_id: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="CREATED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class RbiCompliance(Base):
    __tablename__ = "rbi_compliance"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    loan_id: Mapped[str] = mapped_column(String, ForeignKey("loan.id"))
    total_jewel_count: Mapped[int] = mapped_column(Integer)
    overall_image_id: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RbiComplianceItem(Base):
    __tablename__ = "rbi_compliance_item"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    compliance_id: Mapped[str] = mapped_column(String, ForeignKey("rbi_compliance.id"))
    jewel_index: Mapped[int] = mapped_column(Integer)
    jewel_image_id: Mapped[str] = mapped_column(String)


class PurityTest(Base):
    __tablename__ = "purity_test"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    loan_id: Mapped[str] = mapped_column(String, ForeignKey("loan.id"))
    jewel_index: Mapped[int] = mapped_column(Integer)
    result: Mapped[str] = mapped_column(String)
    confidence_score: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LoanSummary(Base):
    __tablename__ = "loan_summary"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    loan_id: Mapped[str] = mapped_column(String, ForeignKey("loan.id"), unique=True)
    snapshot_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    actor_user_id: Mapped[str | None] = mapped_column(String, nullable=True)
    action: Mapped[str] = mapped_column(String)
    entity_type: Mapped[str] = mapped_column(String)
    entity_id: Mapped[str] = mapped_column(String)
    metadata: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_record"
    __table_args__ = (UniqueConstraint("tenant_id", "key", "endpoint", name="uq_idempotency"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    key: Mapped[str] = mapped_column(String)
    endpoint: Mapped[str] = mapped_column(String)
    request_hash: Mapped[str] = mapped_column(String)
    response_payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, UniqueConstraint
from app.core.database import Base

class IdempotencyRecord(Base):
    __tablename__ = 'idempotency_record'
    __table_args__ = (UniqueConstraint('tenant_id', 'key', 'endpoint', name='uq_idempotency'),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    key: Mapped[str] = mapped_column(String)
    endpoint: Mapped[str] = mapped_column(String)
    request_hash: Mapped[str] = mapped_column(String)
    response_payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

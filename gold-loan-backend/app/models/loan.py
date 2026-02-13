import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime
from app.core.database import Base

class Loan(Base):
    __tablename__ = 'loan'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    customer_id: Mapped[str] = mapped_column(String)
    appraiser_id: Mapped[str] = mapped_column(String)
    bank_id: Mapped[str] = mapped_column(String)
    branch_id: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default='CREATED')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

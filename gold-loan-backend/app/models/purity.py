import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime
from app.core.database import Base

class PurityTest(Base):
    __tablename__ = 'purity_test'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    loan_id: Mapped[str] = mapped_column(String)
    jewel_index: Mapped[int] = mapped_column(Integer)
    result: Mapped[str] = mapped_column(String)
    confidence_score: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from app.core.database import Base

class RbiCompliance(Base):
    __tablename__ = 'rbi_compliance'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    loan_id: Mapped[str] = mapped_column(String)
    total_jewel_count: Mapped[int] = mapped_column(Integer)
    overall_image_id: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class RbiComplianceItem(Base):
    __tablename__ = 'rbi_compliance_item'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    compliance_id: Mapped[str] = mapped_column(String)
    jewel_index: Mapped[int] = mapped_column(Integer)
    jewel_image_id: Mapped[str] = mapped_column(String)

import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime
from app.core.database import Base

class Appraiser(Base):
    __tablename__ = 'appraiser'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    branch_id: Mapped[str] = mapped_column(String)
    appraiser_code: Mapped[str] = mapped_column(String, unique=True)
    face_image_id: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default='ACTIVE')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

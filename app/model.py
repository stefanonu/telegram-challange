from sqlalchemy import Column, String, JSON, Integer, DateTime, UniqueConstraint
from datetime import datetime
from app.db import Base

class JobRecord(Base):
    __tablename__ = "job_records"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, nullable=False, unique=True)
    payload = Column(JSON, nullable=False)
    worker_id = Column(Integer, nullable=True)
    result = Column(String, nullable=True)
    status = Column(String, default="in_progress")
    created_at = Column(DateTime, default=datetime.utcnow)

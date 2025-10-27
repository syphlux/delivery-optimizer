from sqlalchemy import Column, String, Float, Enum, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from enum import Enum as PyEnum

from app.db.postgres import Base


class DriverStatus(PyEnum):
    AVAILABLE = "AVAILABLE"
    DRIVING = "DRIVING"
    UNAVAILABLE = "UNAVAILABLE"


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False, unique=True)
    vehicle_capacity = Column(Integer, nullable=False)
    num_daily_work_hours = Column(Float, nullable=False)
    current_lat = Column(Float, nullable=True)
    current_lon = Column(Float, nullable=True)
    status = Column(Enum(DriverStatus), default=DriverStatus.AVAILABLE, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
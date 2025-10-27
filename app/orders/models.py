import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, UUID
from datetime import datetime, timezone
from enum import Enum as PyEnum
from app.db.postgres import Base

class OrderStatus(PyEnum):
    PENDING = "PENDING"
    IN_ROUTE = "IN_ROUTE"
    IN_RETURN = "IN_RETURN"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_name = Column(String, nullable=False)
    item_id = Column(String, nullable=False)
    pickup_address = Column(String, nullable=False)
    pickup_lat = Column(Float, nullable=False)
    pickup_lon = Column(Float, nullable=False)
    delivery_address = Column(String, nullable=False)
    delivery_lat = Column(Float, nullable=False)
    delivery_lon = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

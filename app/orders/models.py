import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, UUID
from datetime import datetime, timezone, timedelta
from enum import Enum as PyEnum
from app.db.postgres import Base

class OrderStatus(PyEnum):
    PRE_DELIVERY = "PRE_DELIVERY"
    PENDING = "PENDING"
    IN_ROUTE = "IN_ROUTE"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_name = Column(String, nullable=False)
    item_id = Column(String, nullable=False)
    pickup_address = Column(String, nullable=False)
    pickup_lat = Column(Float, nullable=True)
    pickup_lon = Column(Float, nullable=True)
    delivery_address = Column(String, nullable=False)
    delivery_lat = Column(Float, nullable=True)
    delivery_lon = Column(Float, nullable=True)
    available_from = Column(DateTime, default=datetime.now(timezone.utc))
    deadline = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not self.available_from:
            self.available_from = datetime.now(timezone.utc)

        if not self.deadline:
            self.deadline = self.available_from + timedelta(days=3)

        if self.deadline <= self.available_from:
            raise ValueError("Deadline must be after available_from time.")
        
        if not self.status:
            self.status = (
                OrderStatus.PRE_DELIVERY
                if datetime.now(timezone.utc) < self.available_from
                else OrderStatus.PENDING
            )

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.orders.models import Order, OrderStatus
from pydantic import BaseModel
from typing import List


router = APIRouter(prefix="/orders", tags=["orders"])


# ---------- Pydantic Schemas ---------- #
class OrderCreate(BaseModel):
    customer_name: str
    item_id: str

    pickup_address: str
    pickup_lat: float
    pickup_lon: float

    delivery_address: str
    delivery_lat: float
    delivery_lon: float


class OrderRead(BaseModel):
    id: str
    customer_name: str
    item_id: str
    pickup_address: str
    delivery_address: str
    status: str

    class Config:
        orm_mode = True


class OrderStatusUpdate(BaseModel):
    new_status: OrderStatus


# ---------- Routes ---------- #

@router.post("/", response_model=OrderRead)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    new_order = Order(**order.model_dump())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@router.get("/", response_model=List[OrderRead])
def list_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return orders


@router.patch("/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: str = Path(..., description="The ID of the order to update"),
    new_status: OrderStatus = None,
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if new_status is None:
        raise HTTPException(status_code=400, detail="New status must be provided")

    order.status = new_status
    db.commit()
    db.refresh(order)
    return order

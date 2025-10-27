from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.drivers.models import Driver, DriverStatus
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/drivers", tags=["Drivers"])


# ---------- Pydantic Schemas ---------- #
class DriverCreate(BaseModel):
    name: str
    phone_number: str
    vehicle_capacity: int
    num_daily_work_hours: float
    current_lat: Optional[float] = None
    current_lon: Optional[float] = None


class DriverResponse(BaseModel):
    id: UUID
    name: str
    phone_number: str
    vehicle_capacity: int
    num_daily_work_hours: float
    current_lat: Optional[float]
    current_lon: Optional[float]
    status: DriverStatus
    created_at: datetime

    class Config:
        orm_mode = True


class DriverStatusUpdate(BaseModel):
    new_status: DriverStatus


class DriverLocationUpdate(BaseModel):
    lat: float
    lon: float


# ---------- Routes ---------- #

@router.post("/", response_model=DriverResponse)
def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    new_driver = Driver(**driver.model_dump())
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    return new_driver


@router.get("/", response_model=List[DriverResponse])
def list_drivers(db: Session = Depends(get_db)):
    return db.query(Driver).all()


@router.patch("/{driver_id}/status", response_model=DriverResponse)
def update_driver_status(
    driver_id: UUID,
    status_update: DriverStatusUpdate,
    db: Session = Depends(get_db)
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    driver.status = status_update.new_status
    db.commit()
    db.refresh(driver)
    return driver


@router.patch("/{driver_id}/location", response_model=DriverResponse)
def update_driver_location(
    driver_id: str,
    location: DriverLocationUpdate,
    db: Session = Depends(get_db)
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    driver.current_lat = location.lat
    driver.current_lon = location.lon
    db.commit()
    db.refresh(driver)
    return driver

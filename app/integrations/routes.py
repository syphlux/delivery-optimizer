from typing import Dict, List, Tuple
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.orders.models import Order
from app.orders.models import OrderStatus
from app.integrations.google_sheets import get_google_sheet_data
from datetime import datetime, timezone
from uuid import uuid4

router = APIRouter(prefix="/integrations", tags=["Integrations"])

SHEET_ID = "YOUR_SHEET_ID_HERE"
RANGE_NAME = "Orders!A2:G"  # adjust to your sheet structure

@router.post("/sync-from-sheets", summary="Import orders from Google Sheets")
def sync_orders_from_sheets(db: Session = Depends(get_db), batch_size: int = 100):

    def _commit_buffer(db: Session, buffered: List[Order]) -> Tuple[int, int]:
        """Attempt to commit the entire buffer. If it fails, try per-row commit.
        Return (committed, skipped) counts and clear/leave buffer accordingly."""
        if not buffered:
            return 0, 0

        try:
            # Try fast path: commit whole batch at once
            for obj in buffered:
                db.add(obj)
            db.commit()
            return len(buffered), 0
        except Exception as e:
            # Whole-batch commit failed: rollback and try per-row
            db.rollback()
            committed = 0
            skipped = 0
            for idx, obj in enumerate(buffered, start=1):
                try:
                    db.add(obj)
                    db.commit()
                    committed += 1
                except Exception as e_row:
                    db.rollback()
                    skipped += 1
                    # optional: log the error with context
                    print(f"Skipped buffered row #{idx} due to: {e_row}")
            return committed, skipped
        finally:
            # ensure no leftover state
            try:
                db.flush()
            except Exception:
                pass

    """Safely import orders from Google Sheets into PostgreSQL."""
    try:
        sheet_data: List[Dict] = get_google_sheet_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch data from Google Sheets: {str(e)}",
        )

    if not sheet_data:
        return {"imported": 0, "skipped": 0, "message": "No rows found in sheet."}

    buffered = []
    imported_count = 0
    skipped_count = 0

    for idx, row in enumerate(sheet_data, start=1):
        try:
            # --- Validation ---
            required_fields = ["customer_name", "item_id", "pickup_address", "delivery_address"]
            if not all(row.get(field) for field in required_fields):
                skipped_count += 1
                print(f"Row {idx} skipped: missing required fields")
                continue

            order_id = str(row.get("order_id") or uuid4())

            # --- Skip duplicates ---
            if db.query(Order).filter(Order.id == order_id).first():
                skipped_count += 1
                continue

            # --- Parse status safely ---
            raw_status = str(row.get("status", "PENDING")).upper()
            status = (
                OrderStatus[raw_status]
                if raw_status in OrderStatus.__members__
                else OrderStatus.PENDING
            )

            # --- Create Order object ---
            new_order = Order(
                id=order_id,
                customer_name=row["customer_name"],
                pickup_address=row["pickup_address"],
                pickup_lat=_try_parse_float(row.get("pickup_lat")),
                pickup_lon=_try_parse_float(row.get("pickup_lon")),
                delivery_address=row["delivery_address"],
                delivery_lat=_try_parse_float(row.get("delivery_lat")),
                delivery_lon=_try_parse_float(row.get("delivery_lon")),
                item_id=str(row["item_id"]),
                status=status,
                created_at=datetime.now(timezone.utc),
            )

            buffered.append(new_order)

            if len(buffered) >= batch_size:
                committed, skipped = _commit_buffer(db, buffered)
                imported_count += committed
                skipped_count += skipped
                buffered.clear()

        except Exception as e:
            print(f"Row {idx} failed: {e}")
            skipped_count += 1

    if buffered:
        committed, skipped = _commit_buffer(db, buffered)
        imported_count += committed
        skipped_count += skipped
        buffered.clear()
        
    return {
        "imported": imported_count,
        "skipped": skipped_count,
        "message": "Sync complete",
    }


# --- Utility for type-safe parsing ---
def _try_parse_float(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except ValueError:
        return None

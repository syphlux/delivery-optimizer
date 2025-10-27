from fastapi import FastAPI
from app.orders.routes import router as orders_router

app = FastAPI(title="Delivery Optimizer")

@app.get("/")
def read_root():
    return {"message": "Welcome to Delivery Optimizer!"}

app.include_router(orders_router)

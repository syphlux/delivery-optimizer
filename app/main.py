from fastapi import FastAPI
from app.orders.routes import router as orders_router
from app.drivers.routes import router as drivers_router
from app.integrations.routes import router as integrations_router

app = FastAPI(title="Delivery Optimizer", debug=True)

@app.get("/")
def read_root():
    return {"message": "Welcome to Delivery Optimizer!"}

app.include_router(orders_router)
app.include_router(drivers_router)
app.include_router(integrations_router)

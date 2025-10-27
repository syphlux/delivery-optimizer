from app.db.postgres import Base, engine
from app.orders.models import Order
from app.drivers.models import Driver



print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully.")
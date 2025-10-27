from app.db.postgres import Base, engine
from app.orders.models import Order

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully.")
from app.database.base import Base
from app.database.session import engine
import app.models # This ensures all models are registered with Base

def init_db():
    print("Initializing the database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()

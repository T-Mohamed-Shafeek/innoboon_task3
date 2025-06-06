import asyncio
from database import database
from models import metadata
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/ecommerce")

# Create tables
def create_tables():
    engine = create_engine(DATABASE_URL)
    metadata.drop_all(engine)  # Drop existing tables
    metadata.create_all(engine)  # Create new tables
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()

from backend.models import metadata
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
metadata.create_all(engine)
print("Tables created.")
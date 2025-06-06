import os
from databases import Database
from dotenv import load_dotenv
from .config import settings

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
database = Database(settings.DATABASE_URL)
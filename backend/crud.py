from .database import database
from .models import users
from .schemas import UserCreate
from passlib.context import CryptContext
from sqlalchemy import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hashing password before saving to DB
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verifying password for login
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Save new user to DB
async def create_user(user: UserCreate):
    hashed_pw = hash_password(user.password)
    query = users.insert().values(
        name=user.name,
        email=user.email,
        hashed_password=hashed_pw
    )
    user_id = await database.execute(query)
    return { "id": user_id, "name": user.name, "email": user.email }

# Get user by email (for login or validation)
async def get_user_by_email(email: str):
    query = users.select().where(users.c.email == email)
    return await database.fetch_one(query)

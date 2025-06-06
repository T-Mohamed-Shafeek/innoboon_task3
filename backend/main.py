from fastapi import FastAPI, Depends, HTTPException, Header
from .database import database
from .models import metadata
from .crud import create_user, get_user_by_email, verify_password
from .schemas import UserCreate, UserLogin, UserOut
from .auth import create_access_token, verify_access_token
from .middleware import rate_limit_middleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="User Auth API", version="1.0.0")

# Adding rate limiting middleware
app.add_middleware(rate_limit_middleware)

# Configuring CORS with specific origins
origins = os.getenv("ALLOWED_ORIGINS").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    if await get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return await create_user(user)

@app.post("/login")
async def login(user: UserLogin):
    db_user = await get_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"user_id": db_user["id"], "email": db_user["email"]})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
async def get_me(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalid or expired")
    return {"user": payload}

@app.post("/logout")
async def logout(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    return {"message": "Successfully logged out"}
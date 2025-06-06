from pydantic import BaseModel, EmailStr

__all__ = ['UserCreate', 'UserLogin', 'UserOut']

# For user registration
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

# For login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# What we return from the API
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

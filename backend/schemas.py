"""
Pydantic models for request/response validation.
This module defines the data validation schemas used throughout the application.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime
import re

__all__ = ['UserCreate', 'UserLogin', 'UserOut', 'ProductBase', 'ProductCreate', 'ProductUpdate', 'ProductOut', 'OrderItemBase', 'OrderItemCreate', 'OrderItemOut', 'OrderCreate', 'OrderOut']

class UserBase(BaseModel):
    """Base user schema with common attributes."""
    name: str = Field(..., min_length=2, max_length=50, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")

class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, description="User's password")
    
    @validator('password')
    def password_complexity(cls, v):
        """Validate password complexity."""
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', v):
            raise ValueError('Password must contain at least one letter and one number')
        return v

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

class UserOut(UserBase):
    """Schema for user response data."""
    id: int
    is_admin: int = Field(0, ge=0, le=1)

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    """Base category schema with common attributes."""
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)

class CategoryCreate(CategoryBase):
    """Schema for category creation."""
    pass

class CategoryUpdate(CategoryBase):
    """Schema for category update."""
    pass

class CategoryOut(CategoryBase):
    """Schema for category response data."""
    id: int

class ProductBase(BaseModel):
    """Base product schema with common attributes."""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0, description="Product price must be greater than 0")
    stock: int = Field(..., ge=0, description="Product stock must be non-negative")
    image_url: Optional[str] = Field(None, max_length=500)
    category_id: int = Field(..., gt=0)

class ProductCreate(ProductBase):
    """Schema for product creation."""
    pass

class ProductUpdate(ProductBase):
    """Schema for product update."""
    pass

class ProductOut(ProductBase):
    """Schema for product response data."""
    id: int
    category: Optional[CategoryOut] = None

class OrderItemBase(BaseModel):
    """Base order item schema with common attributes."""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    """Schema for order item creation."""
    pass

class OrderItemOut(OrderItemBase):
    """Schema for order item response data."""
    id: int
    price: float = Field(..., gt=0)

class OrderCreate(BaseModel):
    """Schema for order creation."""
    items: List[OrderItemCreate] = Field(..., min_items=1)

class OrderOut(BaseModel):
    """Schema for order response data."""
    id: int
    user_id: int
    status: str = Field(..., pattern="^(pending|completed|cancelled)$")
    total_amount: float
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemOut]

"""
Database models for the e-commerce application.
This module defines the SQLAlchemy models that represent the database tables.
"""

# The ORM 
from sqlalchemy import Table, Column, Integer, String, MetaData, Float, ForeignKey, DateTime, Enum
from datetime import datetime

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False, comment="User's full name"),
    Column("email", String, unique=True, index=True, comment="User's email address"),
    Column("hashed_password", String, nullable=False, comment="Hashed user password"),
    Column("is_admin", Integer, default=0, comment="User role: 0=regular user, 1=admin"),
)

categories = Table(
    "categories",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False, unique=True, comment="Category name"),
    Column("description", String, comment="Category description"),
    Column("image_url", String, comment="URL to category image"),
)

products = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False, comment="Product name"),
    Column("description", String, comment="Product description"),
    Column("price", Float, nullable=False, comment="Product price"),
    Column("stock", Integer, nullable=False, comment="Available stock"),
    Column("image_url", String, comment="URL to product image"),
    Column("category_id", Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key to categories table"
    ),
)

orders = Table(
    "orders",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key to users table"
    ),
    Column(
        "status",
        String,
        nullable=False,
        comment="Order status: pending, completed, cancelled"
    ),
    Column("total_amount", Float, nullable=False, comment="Total order amount"),
    Column(
        "created_at",
        DateTime,
        default=datetime.utcnow,
        comment="Order creation timestamp"
    ),
    Column(
        "updated_at",
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Last update timestamp"
    ),
)

order_items = Table(
    "order_items",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "order_id",
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key to orders table"
    ),
    Column(
        "product_id",
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key to products table"
    ),
    Column("quantity", Integer, nullable=False, comment="Quantity ordered"),
    Column("price", Float, nullable=False, comment="Price at time of purchase"),
)

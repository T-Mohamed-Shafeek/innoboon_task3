from fastapi import FastAPI, Depends, HTTPException, Header, Path, status
from .database import database
from .models import metadata
from .config import settings
from .crud import (
    create_user, create_product, get_product, get_all_products,
    update_product, delete_product, create_order, get_order,
    get_user_orders, update_order_status, create_category,
    get_category, get_all_categories, update_category,
    delete_category, get_products_by_category
)
from .schemas import (
    UserCreate, UserLogin, UserOut,
    ProductCreate, ProductUpdate, ProductOut,
    OrderCreate, OrderOut, CategoryCreate,
    CategoryUpdate, CategoryOut
)
from .auth import create_access_token, verify_access_token, get_current_user, get_user_by_email
from .utils import verify_password
from .middleware import rate_limit_middleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from typing import List
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI(
    title="E-commerce API",
    version="1.0.0",
    description="A modern e-commerce API with authentication and product management"
)

# Adding rate limiting middleware
app.add_middleware(rate_limit_middleware)

# Configuring CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = create_engine(settings.DATABASE_URL)
metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

# Auth endpoints
@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    if await get_user_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return await create_user(user)

@app.post("/login", status_code=status.HTTP_200_OK)
async def login(user: UserLogin):
    db_user = await get_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    token = create_access_token({"user_id": db_user["id"], "email": db_user["email"]})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me", response_model=UserOut)
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.post("/logout")
async def logout(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    return {"message": "Successfully logged out"}

# Product endpoints
@app.post("/products", response_model=ProductOut)
async def add_product(
    product: ProductCreate,
    current_user: dict = Depends(get_current_user)
):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Only admins can add products")
    return await create_product(product)

@app.get("/products", response_model=List[ProductOut])
async def list_products():
    return await get_all_products()

@app.get("/products/{product_id}", response_model=ProductOut)
async def get_single_product(
    product_id: int = Path(..., title="The ID of the product to get")
):
    product = await get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=ProductOut)
async def update_single_product(
    product_id: int,
    product: ProductUpdate,
    current_user: dict = Depends(get_current_user)
):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Only admins can update products")
    existing_product = await get_product(product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return await update_product(product_id, product)

@app.delete("/products/{product_id}")
async def delete_single_product(
    product_id: int,
    current_user: dict = Depends(get_current_user)
):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Only admins can delete products")
    existing_product = await get_product(product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    await delete_product(product_id)
    return {"message": "Product deleted successfully"}

# Order endpoints
@app.post("/orders", response_model=OrderOut)
async def create_new_order(
    order: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        return await create_order(current_user["id"], order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/orders/{order_id}", response_model=OrderOut)
async def get_single_order(
    order_id: int,
    current_user: dict = Depends(get_current_user)
):
    order = await get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order["user_id"] != current_user["id"] and not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    return order

@app.get("/orders", response_model=List[OrderOut])
async def list_user_orders(current_user: dict = Depends(get_current_user)):
    return await get_user_orders(current_user["id"])

@app.put("/orders/{order_id}/status")
async def update_order_status_endpoint(
    order_id: int,
    status: str,
    current_user: dict = Depends(get_current_user)
):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Only admins can update order status")
    order = await get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if status not in ["pending", "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    return await update_order_status(order_id, status)

# Category endpoints
@app.post("/categories", response_model=CategoryOut)
async def add_category(
    category: CategoryCreate,
    current_user: dict = Depends(get_current_user)
):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Only admins can add categories")
    return await create_category(category)

@app.get("/categories", response_model=List[CategoryOut])
async def list_categories():
    return await get_all_categories()

@app.get("/categories/{category_id}", response_model=CategoryOut)
async def get_single_category(
    category_id: int = Path(..., title="The ID of the category to get")
):
    category = await get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.get("/categories/{category_id}/products", response_model=List[ProductOut])
async def get_category_products(
    category_id: int = Path(..., title="The ID of the category to get products for")
):
    category = await get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return await get_products_by_category(category_id)

@app.put("/categories/{category_id}", response_model=CategoryOut)
async def update_single_category(
    category_id: int,
    category: CategoryUpdate,
    current_user: dict = Depends(get_current_user)
):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Only admins can update categories")
    existing_category = await get_category(category_id)
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return await update_category(category_id, category)

@app.delete("/categories/{category_id}")
async def delete_single_category(
    category_id: int,
    current_user: dict = Depends(get_current_user)
):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Only admins can delete categories")
    existing_category = await get_category(category_id)
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")
    await delete_category(category_id)
    return {"message": "Category deleted successfully"}
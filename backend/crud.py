from .database import database
from .models import users, products, orders, order_items, categories
from .schemas import UserCreate, ProductCreate, ProductUpdate, OrderCreate, CategoryCreate, CategoryUpdate
from .utils import get_password_hash
from datetime import datetime
from sqlalchemy import select

# User operations
async def create_user(user: UserCreate, is_admin: bool = False):
    hashed_password = get_password_hash(user.password)
    query = users.insert().values(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        is_admin=1 if is_admin else 0
    )
    user_id = await database.execute(query)
    return {**user.dict(), "id": user_id, "is_admin": 1 if is_admin else 0}

async def get_user_by_email(email: str):
    query = users.select().where(users.c.email == email)
    result = await database.fetch_one(query)
    if result:
        # Ensure is_admin is an integer
        return {
            "id": result["id"],
            "name": result["name"],
            "email": result["email"],
            "hashed_password": result["hashed_password"],
            "is_admin": result["is_admin"] if result["is_admin"] is not None else 0
        }
    return None

# Category operations
async def create_category(category: CategoryCreate):
    query = categories.insert().values(**category.dict())
    category_id = await database.execute(query)
    return {**category.dict(), "id": category_id}

async def get_category(category_id: int):
    query = categories.select().where(categories.c.id == category_id)
    return await database.fetch_one(query)

async def get_all_categories():
    query = categories.select()
    return await database.fetch_all(query)

async def update_category(category_id: int, category: CategoryUpdate):
    query = categories.update().where(categories.c.id == category_id).values(**category.dict())
    await database.execute(query)
    return await get_category(category_id)

async def delete_category(category_id: int):
    query = categories.delete().where(categories.c.id == category_id)
    return await database.execute(query)

# Product operations
async def create_product(product: ProductCreate):
    # Verify category exists
    category = await get_category(product.category_id)
    if not category:
        raise ValueError(f"Category {product.category_id} not found")
    
    query = products.insert().values(**product.dict())
    product_id = await database.execute(query)
    return await get_product(product_id)

async def get_product(product_id: int):
    query = select(
        products,
        categories.c.name.label('category_name'),
        categories.c.description.label('category_description'),
        categories.c.image_url.label('category_image_url')
    ).join(categories).where(products.c.id == product_id)
    
    result = await database.fetch_one(query)
    if result:
        return {
            **dict(result),
            'category': {
                'id': result['category_id'],
                'name': result['category_name'],
                'description': result['category_description'],
                'image_url': result['category_image_url']
            }
        }
    return None

async def get_all_products():
    query = select(
        products,
        categories.c.name.label('category_name'),
        categories.c.description.label('category_description'),
        categories.c.image_url.label('category_image_url')
    ).join(categories)
    
    results = await database.fetch_all(query)
    return [{
        **dict(result),
        'category': {
            'id': result['category_id'],
            'name': result['category_name'],
            'description': result['category_description'],
            'image_url': result['category_image_url']
        }
    } for result in results]

async def get_products_by_category(category_id: int):
    query = select(
        products,
        categories.c.name.label('category_name'),
        categories.c.description.label('category_description'),
        categories.c.image_url.label('category_image_url')
    ).join(categories).where(products.c.category_id == category_id)
    
    results = await database.fetch_all(query)
    return [{
        **dict(result),
        'category': {
            'id': result['category_id'],
            'name': result['category_name'],
            'description': result['category_description'],
            'image_url': result['category_image_url']
        }
    } for result in results]

async def update_product(product_id: int, product: ProductUpdate):
    # Verify category exists
    category = await get_category(product.category_id)
    if not category:
        raise ValueError(f"Category {product.category_id} not found")
    
    query = products.update().where(products.c.id == product_id).values(**product.dict())
    await database.execute(query)
    return await get_product(product_id)

async def delete_product(product_id: int):
    query = products.delete().where(products.c.id == product_id)
    return await database.execute(query)

# Order operations
async def create_order(user_id: int, order: OrderCreate):
    # Start with 0 total amount
    order_values = {
        "user_id": user_id,
        "status": "pending",
        "total_amount": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Create order
    query = orders.insert().values(**order_values)
    order_id = await database.execute(query)
    
    total_amount = 0
    # Create order items and calculate total
    for item in order.items:
        product = await get_product(item.product_id)
        if not product:
            raise ValueError(f"Product {item.product_id} not found")
        if product["stock"] < item.quantity:
            raise ValueError(f"Insufficient stock for product {item.product_id}")
        
        # Calculate item total
        item_price = product["price"]
        item_total = item_price * item.quantity
        total_amount += item_total
        
        # Create order item
        order_item_values = {
            "order_id": order_id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price": item_price
        }
        await database.execute(order_items.insert().values(**order_item_values))
        
        # Update product stock
        new_stock = product["stock"] - item.quantity
        await database.execute(
            products.update()
            .where(products.c.id == item.product_id)
            .values(stock=new_stock)
        )
    
    # Update order with total amount
    await database.execute(
        orders.update()
        .where(orders.c.id == order_id)
        .values(total_amount=total_amount)
    )
    
    return await get_order(order_id)

async def get_order(order_id: int):
    # Get order
    order_query = orders.select().where(orders.c.id == order_id)
    order = await database.fetch_one(order_query)
    if not order:
        return None
    
    # Get order items
    items_query = order_items.select().where(order_items.c.order_id == order_id)
    items = await database.fetch_all(items_query)
    
    return {**dict(order), "items": [dict(item) for item in items]}


async def get_user_orders(user_id: int):
    # Get all orders for the user
    query = orders.select().where(orders.c.user_id == user_id)
    user_orders = await database.fetch_all(query)
    
    # For each order, get its items
    result = []
    for order in user_orders:
        # Get order items
        items_query = order_items.select().where(order_items.c.order_id == order.id)
        items = await database.fetch_all(items_query)
        
        # Convert to dict and ensure datetime fields are properly formatted
        order_dict = dict(order)
        order_dict["created_at"] = order_dict["created_at"].isoformat() if order_dict["created_at"] else None
        order_dict["updated_at"] = order_dict["updated_at"].isoformat() if order_dict["updated_at"] else None
        order_dict["items"] = [dict(item) for item in items]
        
        result.append(order_dict)
    
    return result

# Update order status
async def update_order_status(order_id: int, status: str):
    query = orders.update().where(orders.c.id == order_id).values(
        status=status,
        updated_at=datetime.utcnow()
    )
    await database.execute(query)
    return await get_order(order_id)

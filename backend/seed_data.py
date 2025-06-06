import asyncio
from database import database
from models import categories, products

async def seed_data():
    await database.connect()

    # Sample categories with images
    sample_categories = [
        {
            "name": "Electronics",
            "description": "Latest gadgets and electronic devices",
            "image_url": "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=500"
        },
        {
            "name": "Home & Kitchen",
            "description": "Essential appliances for your home",
            "image_url": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=500"
        },
        {
            "name": "Fashion",
            "description": "Trendy clothing and accessories",
            "image_url": "https://images.unsplash.com/photo-1445205170230-053b83016050?w=500"
        },
        {
            "name": "Books",
            "description": "Best-selling books across genres",
            "image_url": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=500"
        }
    ]

    # Insert categories and store their IDs
    category_ids = {}
    for category in sample_categories:
        query = categories.insert().values(**category)
        category_id = await database.execute(query)
        category_ids[category["name"]] = category_id

    # Sample products for each category
    sample_products = [
        # Electronics
        {
            "name": "Wireless Earbuds",
            "description": "High-quality wireless earbuds with noise cancellation",
            "price": 129.99,
            "stock": 1,
            "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500",
            "category_id": category_ids["Electronics"]
        },
        {
            "name": "Smart Watch",
            "description": "Feature-rich smartwatch with health tracking",
            "price": 199.99,
            "stock": 30,
            "image_url": "https://images.unsplash.com/photo-1544117519-31a4b719223d?w=500",
            "category_id": category_ids["Electronics"]
        },
        # Home & Kitchen
        {
            "name": "Coffee Maker",
            "description": "Programmable coffee maker with thermal carafe",
            "price": 79.99,
            "stock": 25,
            "image_url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=500",
            "category_id": category_ids["Home & Kitchen"]
        },
        {
            "name": "Air Fryer",
            "description": "Digital air fryer with multiple cooking presets",
            "price": 119.99,
            "stock": 40,
            "image_url": "https://images.unsplash.com/photo-1648923574184-3ba7b91c6f8b?w=500",
            "category_id": category_ids["Home & Kitchen"]
        },
        # Fashion
        {
            "name": "Classic Leather Watch",
            "description": "Elegant leather strap watch with minimalist design",
            "price": 89.99,
            "stock": 35,
            "image_url": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500",
            "category_id": category_ids["Fashion"]
        },
        {
            "name": "Sunglasses",
            "description": "UV protection sunglasses with polarized lenses",
            "price": 59.99,
            "stock": 45,
            "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=500",
            "category_id": category_ids["Fashion"]
        },
        # Books
        {
            "name": "The Art of Programming",
            "description": "Comprehensive guide to modern programming practices",
            "price": 49.99,
            "stock": 60,
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500",
            "category_id": category_ids["Books"]
        },
        {
            "name": "Cooking Masterclass",
            "description": "Step-by-step guide to becoming a better cook",
            "price": 34.99,
            "stock": 55,
            "image_url": "https://images.unsplash.com/photo-1589998059171-988d887df646?w=500",
            "category_id": category_ids["Books"]
        }
    ]

    # Insert products
    for product in sample_products:
        query = products.insert().values(**product)
        await database.execute(query)

    await database.disconnect()
    print("Sample data has been added successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data()) 
# E-commerce Application

A simple e-commerce application built with FastAPI and Streamlit.

## Features

- User authentication (register/login)
- Product management (admin only)
- Shopping cart functionality
- Order management
- Admin dashboard
- Responsive product grid
- Order status tracking

## Tech Stack

- Backend: FastAPI
- Frontend: Streamlit
- Database: SQLAlchemy
- Authentication: JWT

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:8501
API_URL=http://localhost:8000
```

4. Initialize the database:
```bash
cd backend
python create_tables.py
```

## Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

2. Start the frontend application (in a new terminal):
```bash
cd frontend
streamlit run app.py
```

3. Access the application:
- Frontend: http://localhost:8501
- Backend API docs: http://localhost:8000/docs

## User Roles

### Regular User
- Browse products
- Add items to cart
- Place orders
- View order history

### Admin User
- All regular user capabilities
- Add/edit/delete products
- Update order statuses
- View all orders

## API Endpoints

### Authentication
- POST /register - Register new user
- POST /login - User login
- GET /me - Get current user
- POST /logout - User logout

### Products
- GET /products - List all products
- POST /products - Add new product (admin only)
- GET /products/{id} - Get single product
- PUT /products/{id} - Update product (admin only)
- DELETE /products/{id} - Delete product (admin only)

### Orders
- POST /orders - Create new order
- GET /orders - List user orders
- GET /orders/{id} - Get single order
- PUT /orders/{id}/status - Update order status (admin only)

## Development

To make a user an admin, you'll need to manually update their `is_admin` field in the database to 1.

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Rate limiting
- CORS protection
- Input validation
- SQL injection protection through SQLAlchemy 
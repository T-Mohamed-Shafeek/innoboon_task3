import streamlit as st
import requests
import re
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 8

def get_auth_header():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return None

def init_session_state():
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'cart' not in st.session_state:
        st.session_state.cart = {}  # product_id: quantity
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = None

def handle_auth():
    if st.session_state.token:
        return True
        
    option = st.radio("Select action", ["Register", "Login"])

    with st.form("auth_form"):
        name = st.text_input("Name") if option == "Register" else None
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        submitted = st.form_submit_button(option)
        
        if submitted:
            if not validate_email(email):
                st.error("Please enter a valid email address")
            elif not validate_password(password):
                st.error("Password must be at least 8 characters long")
            else:
                try:
                    with st.spinner(f"{option}ing..."):
                        if option == "Register":
                            res = requests.post(
                                f"{API_URL}/register", 
                                json={"name": name, "email": email, "password": password}
                            )
                        else:
                            res = requests.post(
                                f"{API_URL}/login", 
                                json={"email": email, "password": password}
                            )
                        
                        if res.status_code == 200:
                            if option == "Login":
                                    data = res.json()
                                    st.session_state.token = data["access_token"]
                                    # Get user info
                                    user_res = requests.get(
                                        f"{API_URL}/me",
                                        headers=get_auth_header()
                                    )
                                    if user_res.status_code == 200:
                                        user_data = user_res.json()
                                        st.session_state.is_admin = user_data.get("is_admin", 0) == 1
                            st.success(f"{option} successful!")
                            st.rerun()
                        else:
                            st.error(res.json().get("detail", "An error occurred"))
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the server. Please try again later.")
        return False
    return True

def show_category_management():
    st.header("Category Management")
    
    # Add new category form
    with st.form("add_category"):
        st.subheader("Add New Category")
        name = st.text_input("Category Name")
        description = st.text_area("Description")
        image_url = st.text_input("Image URL")
        
        if st.form_submit_button("Add Category"):
            try:
                res = requests.post(
                    f"{API_URL}/categories",
                    headers=get_auth_header(),
                    json={
                        "name": name,
                        "description": description,
                        "image_url": image_url
                    }
                )
                if res.status_code == 200:
                    st.success("Category added successfully!")
                    st.rerun()
                else:
                    st.error(res.json().get("detail", "Failed to add category"))
            except requests.exceptions.RequestException:
                st.error("Could not connect to the server")

def show_categories():
    st.header("Product Categories")
    try:
        res = requests.get(f"{API_URL}/categories")
        if res.status_code == 200:
            categories = res.json()
            
            # Display categories in a grid
            cols = st.columns(3)
            for idx, category in enumerate(categories):
                with cols[idx % 3]:
                    st.subheader(category["name"])
                    if category["image_url"]:
                        st.image(category["image_url"], use_container_width=True)
                    st.write(category["description"])
                    
                    if st.button(f"View Products", key=f"cat_{category['id']}"):
                        st.session_state.selected_category = category['id']
                        st.rerun()
                    
                    # Admin controls
                    if st.session_state.is_admin:
                        if st.button(f"Delete Category", key=f"del_cat_{category['id']}"):
                            res = requests.delete(
                                f"{API_URL}/categories/{category['id']}",
                                headers=get_auth_header()
                            )
                            if res.status_code == 200:
                                st.success("Category deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete category")
        else:
            st.error("Failed to fetch categories")
    except requests.exceptions.RequestException:
        st.error("Could not connect to the server")

def show_products():
    # Get category filter from session state
    category_id = st.session_state.get('selected_category')
    
    if category_id:
        # Show products for specific category
        try:
            res = requests.get(f"{API_URL}/categories/{category_id}/products")
            if res.status_code == 200:
                products = res.json()
                category_res = requests.get(f"{API_URL}/categories/{category_id}")
                if category_res.status_code == 200:
                    category = category_res.json()
                    st.header(f"{category['name']} Products")
                    
                    # Add back button
                    if st.button("← Back to Categories"):
                        st.session_state.selected_category = None
                        st.rerun()
            else:
                st.error("Failed to fetch products")
                return
        except requests.exceptions.RequestException:
            st.error("Could not connect to the server")
            return
    else:
        # Show all products
        try:
            res = requests.get(f"{API_URL}/products")
            if res.status_code == 200:
                products = res.json()
                st.header("All Products")
            else:
                st.error("Failed to fetch products")
                return
        except requests.exceptions.RequestException:
            st.error("Could not connect to the server")
            return
    
    # Display products in a grid
    if not products:
        st.write("No products found.")
        return
        
    cols = st.columns(3)
    for idx, product in enumerate(products):
        with cols[idx % 3]:
            st.subheader(product["name"])
            if product["image_url"]:
                st.image(product["image_url"], use_container_width=True)
            st.write(product["description"])
            st.write(f"Price: ${product['price']:.2f}")
            st.write(f"Stock: {product['stock']}")
            
            # Add to cart button
            if st.session_state.token and product["stock"] > 0:
                quantity = st.number_input(
                    f"Quantity for {product['name']}",
                    min_value=1,
                    max_value=product["stock"],
                    key=f"qty_{product['id']}"
                )
                if st.button(f"Add to Cart", key=f"add_{product['id']}"):
                    if product["id"] in st.session_state.cart:
                        st.session_state.cart[product["id"]] += quantity
                    else:
                        st.session_state.cart[product["id"]] = quantity
                    st.success(f"Added {quantity} {product['name']} to cart!")
                    st.rerun()
            
            # Admin controls
            if st.session_state.is_admin:
                if st.button(f"Delete", key=f"del_{product['id']}"):
                    res = requests.delete(
                        f"{API_URL}/products/{product['id']}",
                        headers=get_auth_header()
                    )
                    if res.status_code == 200:
                        st.success("Product deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete product")

def show_product_management():
    st.header("Product Management")
    
    # Get categories for dropdown
    try:
        res = requests.get(f"{API_URL}/categories")
        if res.status_code == 200:
            categories = res.json()
        else:
            st.error("Failed to fetch categories")
            return
    except requests.exceptions.RequestException:
        st.error("Could not connect to the server")
        return
    
    # Add new product form
    with st.form("add_product"):
        st.subheader("Add New Product")
        name = st.text_input("Product Name")
        description = st.text_area("Description")
        price = st.number_input("Price", min_value=0.01, step=0.01)
        stock = st.number_input("Stock", min_value=0, step=1)
        image_url = st.text_input("Image URL")
        category_id = st.selectbox(
            "Category",
            options=[c["id"] for c in categories],
            format_func=lambda x: next((c["name"] for c in categories if c["id"] == x), "Unknown")
        )
        
        if st.form_submit_button("Add Product"):
            try:
                res = requests.post(
                    f"{API_URL}/products",
                    headers=get_auth_header(),
                    json={
                        "name": name,
                        "description": description,
                        "price": price,
                        "stock": stock,
                        "image_url": image_url,
                        "category_id": category_id
                    }
                )
                if res.status_code == 200:
                    st.success("Product added successfully!")
                    st.rerun()
                else:
                    st.error(res.json().get("detail", "Failed to add product"))
            except requests.exceptions.RequestException:
                st.error("Could not connect to the server")

def show_cart():
    if not st.session_state.cart:
        st.write("Your cart is empty")
        return
    
    st.header("Shopping Cart")
    total = 0
    
    # Fetch product details for cart items
    try:
        items_to_remove = []
        for product_id, quantity in st.session_state.cart.items():
            res = requests.get(f"{API_URL}/products/{product_id}")
            if res.status_code == 200:
                product = res.json()
                st.write(f"{product['name']} - Quantity: {quantity} - ${product['price'] * quantity:.2f}")
                total += product['price'] * quantity
                
                if st.button(f"Remove", key=f"remove_{product_id}"):
                    items_to_remove.append(product_id)
            else:
                items_to_remove.append(product_id)
        
        # Remove items marked for deletion
        for item in items_to_remove:
            del st.session_state.cart[item]
        if items_to_remove:
            st.rerun()
        
        st.write(f"Total: ${total:.2f}")
        
        if st.button("Place Order"):
            # Create order items list
            order_items = [
                {"product_id": pid, "quantity": qty}
                for pid, qty in st.session_state.cart.items()
            ]
            
            # Place order
            try:
                res = requests.post(
                    f"{API_URL}/orders",
                    headers=get_auth_header(),
                    json={"items": order_items}
                )
                
                if res.status_code == 200:
                    st.success("Order placed successfully!")
                    st.session_state.cart = {}  # Clear cart
                    st.rerun()
                else:
                    st.error(res.json().get("detail", "Failed to place order"))
            except requests.exceptions.RequestException:
                st.error("Could not connect to the server")
    except requests.exceptions.RequestException:
        st.error("Could not connect to the server")

def show_orders():
    st.header("Your Orders")
    try:
        res = requests.get(f"{API_URL}/orders", headers=get_auth_header())
        if res.status_code == 200:
            orders = res.json()
            for order in orders:
                with st.expander(f"Order #{order['id']} - {order['status']} - ${order['total_amount']:.2f}"):
                    st.write(f"Date: {datetime.fromisoformat(order['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write("Items:")
                    for item in order['items']:
                        product_res = requests.get(f"{API_URL}/products/{item['product_id']}")
                        if product_res.status_code == 200:
                            product = product_res.json()
                            st.write(f"- {product['name']} x {item['quantity']} @ ${item['price']:.2f} each")
                    
                    if st.session_state.is_admin:
                        new_status = st.selectbox(
                            "Update Status",
                            ["pending", "completed", "cancelled"],
                            key=f"status_{order['id']}"
                        )
                        if new_status != order['status']:
                            if st.button("Update Status", key=f"update_{order['id']}"):
                                res = requests.put(
                                    f"{API_URL}/orders/{order['id']}/status",
                                    headers=get_auth_header(),
                                    params={"status": new_status}
                                )
                                if res.status_code == 200:
                                    st.success("Order status updated!")
                                    st.rerun()
                                else:
                                    st.error("Failed to update order status")
        else:
            st.error("Failed to fetch orders")
    except requests.exceptions.RequestException:
        st.error("Could not connect to the server")

def main():
    st.title("E-commerce App")
    init_session_state()
    
    # Sidebar with auth status and logout
    with st.sidebar:
        if st.session_state.token:
            st.success("Logged in")
            if st.button("Logout"):
                st.session_state.token = None
                st.session_state.is_admin = False
                st.session_state.cart = {}
                st.session_state.selected_category = None
                st.rerun()
    
    # Main content
    if handle_auth():
        # Show admin controls
        if st.session_state.is_admin:
            tab1, tab2 = st.tabs(["Categories", "Products"])
            with tab1:
                show_category_management()
            with tab2:
                show_product_management()
        
        # Show categories and products
        if not st.session_state.selected_category:
            show_categories()
        show_products()
        
        # Show cart and orders for logged-in users
        if st.session_state.token:
            show_cart()
            show_orders()

if __name__ == "__main__":
    main()
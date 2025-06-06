import streamlit as st
import requests
import re
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 8

st.title("User Auth App")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None

if st.session_state.token:
    st.success("You are logged in!")
    if st.button("Logout"):
        st.session_state.token = None
        st.rerun()
else:
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
                                st.session_state.token = res.json()["access_token"]
                            st.success(f"{option} successful!")
                            st.rerun()
                        else:
                            st.error(res.json().get("detail", "An error occurred"))
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the server. Please try again later.")
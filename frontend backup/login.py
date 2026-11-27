import streamlit as st
import requests

def login_page():
    st.subheader("Login")

    email = st.text_input("Email").strip()
    password = st.text_input("Password", type="password").strip()

    if st.button("Login"):
        try:
            res = requests.post(
                "http://127.0.0.1:5000/login",
                json={
                    "email": email,
                    "password": password
                }
            )

            data = res.json()
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend. Make sure Flask server is running.")
            return

        except Exception as e:
            st.error(f"Backend error: {e}")
            return

        if data.get("success"):
            st.session_state.user = data["user"]
            st.success("Login successful!")
            st.rerun()

        else:
            st.error(data.get("error", "Invalid credentials"))
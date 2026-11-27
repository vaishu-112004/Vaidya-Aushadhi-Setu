import streamlit as st
import requests

from doctor_dashboard import show_doctor_dashboard
from pharmacist_dashboard import show_pharmacist_dashboard
from patient_dashboard import show_patient_dashboard

# =====================================================
# BASE URL
# =====================================================

BASE_URL = "http://127.0.0.1:5000"

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Vaidya Aushadhi Setu",
    page_icon="💊",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

def set_bg():

    st.markdown(
        """
        <style>

        .stApp{
            background: linear-gradient(
                to right,
                #dbeafe,
                #f0fdf4
            );
        }

        .main-title{
            text-align:center;
            font-size:48px;
            font-weight:bold;
            color:#0f172a;
            margin-bottom:10px;
        }

        .sub-title{
            text-align:center;
            color:#334155;
            font-size:18px;
            margin-bottom:30px;
        }

        .card{
            background:white;
            padding:25px;
            border-radius:18px;
            box-shadow:0px 0px 15px rgba(0,0,0,0.08);
        }

        .stButton button{
            width:100%;
            border-radius:12px;
            height:45px;
            font-size:17px;
            background:#2563eb;
            color:white;
            border:none;
        }

        .stButton button:hover{
            background:#1d4ed8;
            color:white;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

set_bg()

# =====================================================
# SESSION STATE
# =====================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =====================================================
# LOGIN PAGE
# =====================================================

def login_page():

    st.markdown(
        "<div class='main-title'>💊 Vaidya Aushadhi Setu</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='sub-title'>Blockchain Based Smart Prescription System</div>",
        unsafe_allow_html=True
    )

    with st.container():

        st.markdown(
            "<div class='card'>",
            unsafe_allow_html=True
        )

        st.subheader("Login")

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            if not email or not password:

                st.warning("Please enter email and password")

                return

            try:

                response = requests.post(
                    f"{BASE_URL}/login",
                    json={
                        "email": email,
                        "password": password
                    },
                    timeout=10
                )

                data = response.json()

                # DEBUG
                st.write(data)

                # ---------------- SUCCESS
                if data.get("success"):

                    user = data.get("user")

                    if not user:

                        st.error("User data missing")
                        return

                    # SAVE SESSION
                    st.session_state.logged_in = True

                    st.session_state.user = user

                    st.success("Login successful")

                    st.rerun()

                # ---------------- FAILED
                else:

                    st.error(
                        data.get(
                            "error",
                            "Login failed"
                        )
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Backend server not running"
                )

            except Exception as e:

                st.error(f"Error: {e}")

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

# =====================================================
# SIGNUP PAGE
# =====================================================

def signup_page():

    st.markdown(
        "<div class='main-title'>Create Account</div>",
        unsafe_allow_html=True
    )

    with st.container():

        st.markdown(
            "<div class='card'>",
            unsafe_allow_html=True
        )

        st.subheader("Signup")

        name = st.text_input("Full Name")

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        role = st.selectbox(
            "Role",
            [
                "doctor",
                "patient",
                "pharmacist"
            ]
        )

        aadhaar = None

        license_no = None

        license_expiry = None

        # ---------------- PATIENT
        if role == "patient":

            aadhaar = st.text_input(
                "Aadhaar Number"
            )

        # ---------------- DOCTOR / PHARMACIST
        else:

            license_no = st.text_input(
                "License Number"
            )

            license_expiry = st.date_input(
                "License Expiry Date"
            )

        # ---------------- SIGNUP BUTTON
        if st.button("Create Account"):

            if not name or not email or not password:

                st.warning("Please fill all fields")

                return

            try:

                payload = {

                    "name": name,

                    "email": email,

                    "password": password,

                    "role": role,

                    "aadhaar": aadhaar,

                    "license_no": license_no,

                    "license_expiry": (
                        str(license_expiry)
                        if license_expiry
                        else None
                    )
                }

                response = requests.post(
                    f"{BASE_URL}/signup",
                    json=payload,
                    timeout=10
                )

                data = response.json()

                # DEBUG
                st.write(data)

                if data.get("success"):

                    st.success(
                        "Account created successfully"
                    )

                else:

                    st.error(
                        data.get(
                            "error",
                            "Signup failed"
                        )
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Backend server not running"
                )

            except Exception as e:

                st.error(f"Error: {e}")

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

# =====================================================
# LOGOUT
# =====================================================

def logout():

    st.session_state.user = None

    st.session_state.logged_in = False

    st.rerun()

# =====================================================
# MAIN APP
# =====================================================

if not st.session_state.logged_in:

    menu = st.sidebar.selectbox(
        "Menu",
        [
            "Login",
            "Signup"
        ]
    )

    if menu == "Login":

        login_page()

    else:

        signup_page()

# =====================================================
# DASHBOARD
# =====================================================

else:

    try:

        user = st.session_state.user

        # DEBUG
        st.write("Logged User:", user)

        if not user:

            st.error("User session missing")
            st.stop()

        st.sidebar.success(
            f"{user.get('name')} ({user.get('role')})"
        )

        st.sidebar.markdown("---")

        if st.sidebar.button("Logout"):

            logout()

        role = user.get("role")

        # ---------------- DOCTOR
        if role == "doctor":

            show_doctor_dashboard(user)

        # ---------------- PHARMACIST
        elif role == "pharmacist":

            show_pharmacist_dashboard(user)

        # ---------------- PATIENT
        elif role == "patient":

            show_patient_dashboard(user)

        else:

            st.error("Invalid role")

    except Exception as e:

        st.error(f"Dashboard Error: {e}")
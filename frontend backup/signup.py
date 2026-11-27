import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:5000"

def show():

    st.subheader("Signup")

    name = st.text_input("Full Name")

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    role = st.selectbox(
        "Role",
        ["doctor", "patient", "pharmacist"]
    )

    # ---------------- PATIENT
    aadhaar = None

    # ---------------- DOCTOR/PHARMACIST
    license_no = None
    license_expiry = None

    # PATIENT INPUTS
    if role == "patient":

        aadhaar = st.text_input(
            "Aadhaar Number"
        )

    # DOCTOR/PHARMACIST INPUTS
    else:

        license_no = st.text_input(
            "License Number"
        )

        license_expiry = st.date_input(
            "License Expiry Date"
        )

    # ---------------- SIGNUP BUTTON
    if st.button("Signup"):

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

        try:

            res = requests.post(
                f"{BASE_URL}/signup",
                json=payload
            )

            data = res.json()

            if data.get("success"):

                st.success(
                    "Signup successful"
                )

            else:

                st.error(
                    data.get(
                        "error",
                        "Signup failed"
                    )
                )

        except Exception as e:

            st.error(str(e))
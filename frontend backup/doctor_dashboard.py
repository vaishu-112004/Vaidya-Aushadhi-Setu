import streamlit as st
import requests
import pandas as pd
import base64
from PIL import Image
import io

BASE_URL = "http://127.0.0.1:5000"


def show_doctor_dashboard(user):

    st.title("👨‍⚕ Doctor Dashboard")

    tab1, tab2 = st.tabs(["Create Prescription", "Past Patients"])

    # ---------------- CREATE PRESCRIPTION
    with tab1:

        patient_id = st.number_input("Patient ID", min_value=1, step=1)
        medicine_count = st.number_input("Number of Medicines", 1, 10, 1)

        medicines = []

        for i in range(int(medicine_count)):

            st.markdown(f"### Medicine {i+1}")

            name = st.text_input(f"Name {i}")
            dosage = st.text_input(f"Dosage {i}")
            morning = st.checkbox(f"Morning {i}")
            afternoon = st.checkbox(f"Afternoon {i}")
            night = st.checkbox(f"Night {i}")
            days = st.number_input(f"Days {i}", 1, 30, 1)
            instructions = st.text_area(f"Instructions {i}")

            if name:
                medicines.append({
                    "medicine_name": name,
                    "dosage": dosage,
                    "morning": morning,
                    "afternoon": afternoon,
                    "night": night,
                    "duration_days": days,
                    "instructions": instructions
                })

        if st.button("Generate Prescription"):

            res = requests.post(
                f"{BASE_URL}/create_prescription",
                json={
                    "doctor_id": user["id"],
                    "patient_id": patient_id,
                    "medicines": medicines
                }
            )

            data = res.json()

            if data.get("success"):

                st.success("Prescription Created")

                qr_bytes = base64.b64decode(data["qr"])
                st.image(qr_bytes)

                st.code(data["ipfs_hash"])

            else:
                st.error(data.get("error", "Error"))


    # ---------------- PAST PATIENTS
    with tab2:

        st.subheader("Past Patients")

        res = requests.get(f"{BASE_URL}/doctor_history/{user['id']}")
        data = res.json()

        if data.get("success"):

            df = pd.DataFrame(data["patients"])
            st.dataframe(df)

        else:
            st.warning("No patients found")
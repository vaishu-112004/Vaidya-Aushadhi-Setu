import streamlit as st
import requests
import base64

BASE_URL = "http://127.0.0.1:5000"

def show_patient_dashboard(user):

    st.title("🧑 Patient Dashboard")

    try:

        response = requests.get(
            f"{BASE_URL}/patient_prescription/{user['id']}"
        )

        data = response.json()

        # DEBUG
        st.write(data)

        if data.get("success"):

            st.subheader("Prescription QR")

            qr_bytes = base64.b64decode(
                data["qr"]
            )

            st.image(qr_bytes)

            st.subheader("IPFS Hash")

            st.code(data["ipfs_hash"])

            st.subheader("Blockchain Transaction")

            st.code(data["blockchain_tx"])

            # DELIVERY STATUS
            if data["delivered"]:

                st.success(
                    f"Medicines delivered by {data['delivered_by']}"
                )

            else:

                st.warning(
                    "Medicines not delivered yet"
                )

        else:

            st.info(
                data.get(
                    "error",
                    "No prescription found"
                )
            )

    except Exception as e:

        st.error(str(e))
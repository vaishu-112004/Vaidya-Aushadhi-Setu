import streamlit as st
import requests
import cv2
import numpy as np
import pandas as pd
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://127.0.0.1:5000"


# ---------------- EXTRACT HASH
def extract_ipfs_hash(qr_text):
    try:
        if "hash=" in qr_text:
            parsed = urlparse(qr_text)
            params = parse_qs(parsed.query)
            return params.get("hash")[0]

        return qr_text

    except Exception:
        return None


# ---------------- QR DECODER
def decode_qr(image_bytes):
    file_bytes = np.asarray(bytearray(image_bytes), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)

    return data if data else None


# ---------------- DASHBOARD
def show_pharmacist_dashboard(user):

    st.title("💊 Pharmacist Dashboard")
    st.subheader("Scan Patient QR")

    option = st.radio("Choose Method", ["Upload QR Image", "Camera Scan"])

    qr_data = None

    # ---------------- UPLOAD
    if option == "Upload QR Image":
        qr_file = st.file_uploader("Upload QR", type=["png", "jpg", "jpeg"])

        if qr_file:
            qr_data = decode_qr(qr_file.read())

    # ---------------- CAMERA
    else:
        camera = st.camera_input("Snapshot")

        if camera:
            qr_data = decode_qr(camera.getvalue())

    # ---------------- AFTER SCAN
    if qr_data:

        st.success("QR Scanned")

        ipfs_hash = extract_ipfs_hash(qr_data)

        if not ipfs_hash:
            st.error("Invalid QR Code")
            return

        try:
            # ---------------- SAFE API CALL
            res = requests.get(f"{BASE_URL}/scan/{ipfs_hash}")

            # ❗ SAFE JSON HANDLING (FIX YOUR ERROR)
            try:
                data = res.json()
            except Exception:
                st.error("Backend is not returning JSON")
                st.write("RAW RESPONSE:", res.text)
                return

            # ---------------- VALIDATION
            if not data.get("success"):
                st.error(data.get("error", "Unknown error"))
                return

            prescription = data.get("prescription", {})

            st.subheader("Prescription Details")

            st.write(f"Doctor ID: {prescription.get('doctor_id')}")
            st.write(f"Patient ID: {prescription.get('patient_id')}")

            medicines = prescription.get("medicines", [])

            if medicines:
                df = pd.DataFrame(medicines)
                st.table(df)
            else:
                st.info("No medicines found")

            # ---------------- DELIVERY BUTTON
            if st.button("Medicines Delivered"):

                try:
                    delivered = requests.post(
                        f"{BASE_URL}/mark_delivered",
                        json={
                            "ipfs_hash": ipfs_hash,
                            "pharmacist_name": user["name"]
                        }
                    )

                    try:
                        result = delivered.json()
                    except:
                        st.error("Backend error in delivery API")
                        return

                    if result.get("success"):
                        st.success("Delivery marked successfully")
                    else:
                        st.error(result.get("error", "Failed"))

                except Exception as e:
                    st.error(str(e))

        except Exception as e:
            st.error(str(e))
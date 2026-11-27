import qrcode
import io

from db import connect_db
from ipfs_storage import upload_to_ipfs
from blockchain import store_on_blockchain

# ---------------- CREATE PRESCRIPTION
def create_prescription(
    doctor_id,
    patient_id,
    medicines
):

    prescription = {

        "doctor_id": doctor_id,

        "patient_id": patient_id,

        "medicines": medicines

    }

    # ---------------- UPLOAD TO IPFS
    ipfs_hash = upload_to_ipfs(
        prescription
    )

    # ---------------- STORE BLOCKCHAIN
    tx_hash = store_on_blockchain(
        ipfs_hash
    )

    # ---------------- DB
    db = connect_db()

    cursor = db.cursor()

    # ---------------- INSERT PRESCRIPTION
    prescription_query = """
    INSERT INTO prescriptions
    (
        doctor_id,
        patient_id,
        ipfs_hash,
        blockchain_tx
    )
    VALUES (%s,%s,%s,%s)
    """

    cursor.execute(
        prescription_query,
        (
            doctor_id,
            patient_id,
            ipfs_hash,
            tx_hash
        )
    )

    # ---------------- GET PRESCRIPTION ID
    prescription_id = cursor.lastrowid

    # ---------------- INSERT MEDICINES
    medicine_query = """
    INSERT INTO medicines
    (
        prescription_id,
        medicine_name,
        dosage,
        morning,
        afternoon,
        night,
        duration_days,
        instructions
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """

    for med in medicines:

        cursor.execute(

            medicine_query,

            (
                prescription_id,

                med.get("medicine_name"),

                med.get("dosage"),

                int(med.get("morning", False)),

                int(med.get("afternoon", False)),

                int(med.get("night", False)),

                med.get("duration_days"),

                med.get("instructions")
            )
        )

    # ---------------- SAVE
    db.commit()

    cursor.close()

    db.close()

    return ipfs_hash

# ---------------- GENERATE QR
def generate_qr(ipfs_hash):

    img = qrcode.make(ipfs_hash)

    buf = io.BytesIO()

    img.save(
        buf,
        format="PNG"
    )

    return buf.getvalue()
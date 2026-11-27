
import mysql.connector
import hashlib
from datetime import date

# =====================================================
# DATABASE CONNECTION
# =====================================================

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="vaishu",
        password="Vaishu112004",
        database="vaidya_setu",
        auth_plugin="mysql_native_password"
    )


# =====================================================
# PASSWORD HASHING
# =====================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# =====================================================
# SIGNUP
# =====================================================

def signup(
    name,
    email,
    password,
    role,
    aadhaar=None,
    license_no=None,
    license_expiry=None
):
    db = None
    cursor = None

    try:
        db = connect_db()
        cursor = db.cursor(dictionary=True)

        # Normalize optional fields
        aadhaar = aadhaar or None
        license_no = license_no or None
        license_expiry = license_expiry or None

        # Patients do not need professional licenses
        if role == "patient":
            license_no = None
            license_expiry = None

        # Validate license date format
        if license_expiry:
            try:
                license_expiry = date.fromisoformat(
                    str(license_expiry)
                )
            except ValueError:
                return {
                    "success": False,
                    "error": "Invalid license expiry date. Use YYYY-MM-DD."
                }

        # Check existing email
        cursor.execute(
            "SELECT id FROM users WHERE email=%s",
            (email,)
        )

        if cursor.fetchone():
            return {
                "success": False,
                "error": "Email already exists"
            }

        hashed = hash_password(password)

        verified = True

        # Check license expiry for professional roles
        if role in ["doctor", "pharmacist"]:
            if not license_no or not license_expiry:
                return {
                    "success": False,
                    "error": "License number and expiry date are required."
                }

            if license_expiry < date.today():
                verified = False

        # Insert user
        query = """
            INSERT INTO users
            (
                name,
                email,
                password,
                role,
                aadhaar,
                license_no,
                license_expiry,
                is_verified
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            name,
            email,
            hashed,
            role,
            aadhaar,
            license_no,
            license_expiry,
            verified
        )

        cursor.execute(query, values)
        db.commit()

        return {
            "success": True,
            "message": "Signup successful",
            "user_id": cursor.lastrowid
        }

    except Exception as e:
        if db:
            db.rollback()

        print("DATABASE SIGNUP ERROR:", str(e))

        return {
            "success": False,
            "error": str(e)
        }

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# =====================================================
# LOGIN
# =====================================================

def login_user(email, password):
    db = None
    cursor = None

    try:
        db = connect_db()
        cursor = db.cursor(dictionary=True)

        hashed = hash_password(password)

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                role,
                is_verified,
                license_expiry
            FROM users
            WHERE email=%s
            AND password=%s
        """, (email, hashed))

        user = cursor.fetchone()

        if not user:
            return {
                "success": False,
                "error": "Invalid credentials"
            }

        if (
            user["role"] in ["doctor", "pharmacist"]
            and user["license_expiry"]
        ):
            if str(user["license_expiry"]) < str(date.today()):
                return {
                    "success": False,
                    "error": "License expired"
                }

        return {
            "success": True,
            "user": user,
            "role": user["role"],
            "user_id": user["id"],
            "name": user["name"]
        }

    except Exception as e:
        print("LOGIN ERROR:", str(e))
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# =====================================================
# SAVE PRESCRIPTION
# =====================================================

def save_prescription(
    doctor_id,
    patient_id,
    ipfs_hash,
    blockchain_tx
):
    db = connect_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            INSERT INTO prescriptions
            (
                doctor_id,
                patient_id,
                ipfs_hash,
                blockchain_tx
            )
            VALUES (%s,%s,%s,%s)
        """, (
            doctor_id,
            patient_id,
            ipfs_hash,
            blockchain_tx
        ))

        db.commit()
        return cursor.lastrowid

    finally:
        cursor.close()
        db.close()


# =====================================================
# GET PATIENT PRESCRIPTION
# =====================================================

def get_patient_prescription(patient_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM prescriptions
            WHERE patient_id=%s
            ORDER BY id DESC
            LIMIT 1
        """, (patient_id,))

        return cursor.fetchone()

    finally:
        cursor.close()
        db.close()


# =====================================================
# GET DOCTOR HISTORY
# =====================================================

def get_doctor_history(doctor_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.id,
                p.patient_id,
                u.name AS patient_name,
                p.ipfs_hash,
                p.delivered,
                p.delivered_by,
                p.delivered_at
            FROM prescriptions p
            JOIN users u ON p.patient_id = u.id
            WHERE p.doctor_id=%s
            ORDER BY p.id DESC
        """, (doctor_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        db.close()


# =====================================================
# MARK DELIVERED
# =====================================================

def mark_delivered(ipfs_hash, pharmacist_name):
    db = connect_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            UPDATE prescriptions
            SET delivered=TRUE,
                delivered_by=%s,
                delivered_at=NOW()
            WHERE ipfs_hash=%s
        """, (pharmacist_name, ipfs_hash))

        db.commit()
        return cursor.rowcount > 0

    finally:
        cursor.close()
        db.close()

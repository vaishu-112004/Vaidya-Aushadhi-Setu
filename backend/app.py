
from flask import Flask, request, jsonify
from db import signup, login_user, connect_db
from prescription import create_prescription, generate_qr
import base64

app = Flask(__name__)

# ==============================
# CORS CONFIGURATION
# Allows your HTML frontend to connect to Flask
# ==============================

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ==============================
# HOME / BACKEND HEALTH CHECK
# ==============================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Vaidya Aushadhi Setu Backend is Running!",
        "port": 5000
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "success": True,
        "message": "Backend connected successfully"
    })


# ==============================
# SIGNUP
# ==============================


# ==============================
# SIGNUP
# ==============================

@app.route("/signup", methods=["POST"])
def signup_api():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid or missing JSON data"
            }), 400

        required_fields = ["name", "email", "password", "role"]

        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "error": f"{field} is required"
                }), 400

        role = data["role"].strip().lower()

        if role not in ["patient", "doctor", "pharmacist"]:
            return jsonify({
                "success": False,
                "error": "Invalid role selected"
            }), 400

        # Convert empty values into SQL NULL
        aadhaar = data.get("aadhaar") or None
        license_no = data.get("license_no") or None
        license_expiry = data.get("license_expiry") or None

        # Patients do not require a professional license
        if role == "patient":
            license_no = None
            license_expiry = None

        res = signup(
            name=data["name"].strip(),
            email=data["email"].strip().lower(),
            password=data["password"],
            role=role,
            aadhaar=aadhaar,
            license_no=license_no,
            license_expiry=license_expiry
        )

        status_code = 200 if res.get("success") else 400
        return jsonify(res), status_code

    except Exception as e:
        print("SIGNUP ERROR:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==============================
# LOGIN
# ==============================

@app.route("/login", methods=["POST"])
def login_api():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid or missing JSON data"
            }), 400

        if not data.get("email") or not data.get("password"):
            return jsonify({
                "success": False,
                "error": "Email and password are required"
            }), 400

        res = login_user(
            data["email"],
            data["password"]
        )

        return jsonify(res)

    except Exception as e:
        print("LOGIN ERROR:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==============================
# CREATE PRESCRIPTION
# ==============================

@app.route("/create_prescription", methods=["POST"])
def create_prescription_api():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid or missing JSON data"
            }), 400

        required_fields = [
            "doctor_id",
            "patient_id",
            "medicines"
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"{field} is required"
                }), 400

        ipfs_hash = create_prescription(
            data["doctor_id"],
            data["patient_id"],
            data["medicines"]
        )

        qr = generate_qr(ipfs_hash)
        qr_base64 = base64.b64encode(qr).decode("utf-8")

        return jsonify({
            "success": True,
            "message": "Prescription created successfully",
            "ipfs_hash": ipfs_hash,
            "qr": qr_base64
        })

    except Exception as e:
        print("CREATE PRESCRIPTION ERROR:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==============================
# PATIENT PRESCRIPTION
# ==============================

@app.route("/patient_prescription/<int:patient_id>", methods=["GET"])
def patient_prescription(patient_id):
    db = None
    cursor = None

    try:
        db = connect_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                ipfs_hash,
                blockchain_tx,
                delivered,
                delivered_by
            FROM prescriptions
            WHERE patient_id = %s
            ORDER BY id DESC
            LIMIT 1
        """, (patient_id,))

        data = cursor.fetchone()

        if not data:
            return jsonify({
                "success": False,
                "error": "No prescription found"
            }), 404

        qr = generate_qr(data["ipfs_hash"])
        qr_base64 = base64.b64encode(qr).decode("utf-8")

        return jsonify({
            "success": True,
            "ipfs_hash": data["ipfs_hash"],
            "blockchain_tx": data["blockchain_tx"],
            "delivered": data["delivered"],
            "delivered_by": data["delivered_by"],
            "qr": qr_base64
        })

    except Exception as e:
        print("PATIENT PRESCRIPTION ERROR:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# ==============================
# DOCTOR HISTORY
# ==============================

@app.route("/doctor_history/<int:doctor_id>", methods=["GET"])
def doctor_history(doctor_id):
    db = None
    cursor = None

    try:
        db = connect_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                patient_id,
                ipfs_hash,
                blockchain_tx
            FROM prescriptions
            WHERE doctor_id = %s
            ORDER BY id DESC
        """, (doctor_id,))

        rows = cursor.fetchall()

        return jsonify({
            "success": True,
            "patients": rows
        })

    except Exception as e:
        print("DOCTOR HISTORY ERROR:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# ==============================
# SCAN / VERIFY PRESCRIPTION
# ==============================

@app.route("/scan/<ipfs_hash>", methods=["GET"])
def scan(ipfs_hash):
    try:
        from ipfs_storage import get_prescription_from_ipfs

        data = get_prescription_from_ipfs(ipfs_hash)

        if not data:
            return jsonify({
                "success": False,
                "error": "No prescription found in IPFS"
            }), 404

        return jsonify({
            "success": True,
            "prescription": data
        })

    except Exception as e:
        print("SCAN ERROR:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==============================
# MARK MEDICINE AS DELIVERED
# ==============================

@app.route("/mark_delivered", methods=["POST"])
def mark_delivered():
    db = None
    cursor = None

    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid or missing JSON data"
            }), 400

        ipfs_hash = data.get("ipfs_hash")
        pharmacist_name = data.get("pharmacist_name")

        if not ipfs_hash or not pharmacist_name:
            return jsonify({
                "success": False,
                "error": "IPFS hash and pharmacist name are required"
            }), 400

        db = connect_db()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE prescriptions
            SET
                delivered = 1,
                delivered_by = %s,
                delivered_at = NOW()
            WHERE ipfs_hash = %s
        """, (pharmacist_name, ipfs_hash))

        if cursor.rowcount == 0:
            db.rollback()
            return jsonify({
                "success": False,
                "error": "Prescription not found"
            }), 404

        db.commit()

        return jsonify({
            "success": True,
            "message": "Prescription marked as delivered"
        })

    except Exception as e:
        if db:
            db.rollback()

        print("MARK DELIVERED ERROR:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# ==============================
# RUN FLASK SERVER
# ==============================

if __name__ == "__main__":
    print("---------------------------------------")
    print(" VAIDYA AUSHADHI SETU BACKEND")
    print(" Starting Flask Server...")
    print("---------------------------------------")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )

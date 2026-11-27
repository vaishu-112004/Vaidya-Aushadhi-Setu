import hashlib
from db import connect_db

def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()

def signup(name,email,password,role,aadhaar):

    db = connect_db()
    cursor = db.cursor()

    hashed = hash_password(password)

    cursor.execute(
    "INSERT INTO users(name,email,password,role,aadhaar) VALUES(%s,%s,%s,%s,%s)",
    (name,email,hashed,role,aadhaar)
    )

    db.commit()

def login(email,password):

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    hashed = hash_password(password)

    cursor.execute(
    "SELECT * FROM users WHERE email=%s AND password=%s",
    (email,hashed)
    )

    return cursor.fetchone()





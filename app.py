from flask import Flask, request, jsonify, make_response
import sqlite3
import hashlib
from werkzeug.exceptions import HTTPException
import os
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

DATABASE = 'db/users.db'

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        app.logger.error(f"db connection failed. please check this reason: {e}")
        raise

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_password(password):
    errors = {
        "length": len(password) >= 8,
        "special_char": bool(re.search(r"\W", password)),
        "number": bool(re.search(r"\d", password)),
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "lowercase": bool(re.search(r"[a-z]", password))
    }
    return errors


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    hashed_password = hash_password(password)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password))
        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except sqlite3.Error as e:
        app.logger.error(f"Login error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    password_errors = validate_password(password)
    if not all(password_errors.values()):
        return jsonify({"password_errors": password_errors}), 400

    hashed_password = hash_password(password)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cursor.fetchone() is not None:
            return jsonify({"error": "Email already registered"}), 400

        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
        conn.commit()
        conn.close()

        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.Error as e:
        app.logger.error(f"Registration error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = jsonify({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.errorhandler(Exception)
def handle_general_exception(e):
    app.logger.error(f"Unexpected error: {e}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    if not os.path.exists(os.path.dirname(DATABASE)):
        os.makedirs(os.path.dirname(DATABASE))
    app.run(host="0.0.0.0", port=5000, debug=True)

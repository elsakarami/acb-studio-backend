from flask import Flask, request, jsonify
import sqlite3
import hashlib
from werkzeug.exceptions import HTTPException
from model import train_spam_model 
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

DATABASE = 'db/users.db'


def get_db_connection():
    try:
        connct = sqlite3.connect(DATABASE)
        connct.row_factory = sqlite3.Row
        return connct
    except sqlite3.Error as e:
        app.logger.error(f"db connection failed. please check this reason: {e}")
        raise

def hash_password(password):
    """return sha-256 hash of this password."""
    return hashlib.sha256(password.encode()).hexdigest()

spam_clf, vectorizer = train_spam_model()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    email_vector = vectorizer.transform([email])
    prediction = spam_clf.predict(email_vector)
    if prediction[0] == 1: 
        return jsonify({"error": "Spam email detected, registration blocked"}), 400
    
    hashed_password = hash_password(password)
    
    try:
        connct = get_db_connection()
        cursor = connct.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cursor.fetchone() is not None:
            return jsonify({"error": "Email already registered"}), 400

        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
        connct.commit()
        connct.close()

        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.Error as e:
        app.logger.error(f"Registration error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Handle HTTP exceptions with a JSON response."""
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
    """Handle non-HTTP exceptions with a JSON response."""
    app.logger.error(f"Unexpected error: {e}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    if not os.path.exists(os.path.dirname(DATABASE)):
        os.makedirs(os.path.dirname(DATABASE))
    app.run(host="0.0.0.0", port=5000, debug=True)

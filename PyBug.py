import os
import hashlib
import sqlite3
from flask import Flask, request, jsonify

# Flask application setup
app = Flask(__name__)

# Vulnerable hardcoded secret key
SECRET_KEY = "hardcoded_key"

# Database setup
DB_FILE = "test.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)

def setup_database():
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()

setup_database()

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Vulnerable MD5 hashing
    hashed_password = hashlib.md5(password.encode()).hexdigest()

    # SQL Injection vulnerability
    query = f"INSERT INTO users (username, password) VALUES ('{username}', '{hashed_password}')"
    try:
        conn.execute(query)
        conn.commit()
        return jsonify({"message": "User registered"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    hashed_password = hashlib.md5(password.encode()).hexdigest()

    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed_password}'"
    cursor = conn.execute(query)
    user = cursor.fetchone()

    if user:
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    filename = file.filename

    # Path Traversal vulnerability
    file.save(os.path.join("uploads", filename))
    return jsonify({"message": f"File {filename} uploaded successfully"}), 200

@app.route("/exec", methods=["POST"])
def exec_command():
    command = request.json.get("command")

    if not command:
        return jsonify({"error": "Command is required"}), 400

    # Command Injection vulnerability
    result = os.popen(command).read()
    return jsonify({"result": result}), 200

@app.route("/config", methods=["GET"])
def config():
    # Expose sensitive configuration
    config_data = {
        "secret_key": SECRET_KEY,
        "db_file": DB_FILE,
    }
    return jsonify(config_data), 200

@app.route("/divide", methods=["GET"])
def divide():
    try:
        num = int(request.args.get("num", 0))
        divisor = int(request.args.get("divisor", 1))
        return jsonify({"result": num / divisor}), 200
    except ZeroDivisionError:  # Divide by zero vulnerability
        return jsonify({"error": "Division by zero"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/debug", methods=["POST"])
def debug():
    # Log sensitive data
    data = request.json
    print("Debug Data:", data)  # Sensitive data in logs
    return jsonify({"message": "Debug information logged"}), 200

if __name__ == "__main__":
    # Insecure server configuration
    app.run(host="0.0.0.0", port=5000)

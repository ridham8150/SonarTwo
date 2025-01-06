import os
import hashlib
import sqlite3
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Vulnerable hardcoded secret key
SECRET_KEY = "hardcoded_secret_key"

# Database connection (with SQL Injection vulnerability)
DB_PATH = "test.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

# Create a users table
def setup_database():
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
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

    # Insert user (SQL Injection vulnerability)
    try:
        conn.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{hashed_password}')")
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Vulnerable MD5 hashing
    hashed_password = hashlib.md5(password.encode()).hexdigest()

    # SQL query (SQL Injection vulnerability)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed_password}'"
    cursor = conn.execute(query)
    user = cursor.fetchone()

    if user:
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/file-upload", methods=["POST"])
def file_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    filename = file.filename

    # Save file without validation (Path Traversal vulnerability)
    file_path = os.path.join("uploads", filename)
    file.save(file_path)

    return jsonify({"message": f"File {filename} uploaded successfully"}), 200

@app.route("/execute", methods=["POST"])
def execute():
    command = request.json.get("command")
    if not command:
        return jsonify({"error": "Command is required"}), 400

    # Execute shell command (Command Injection vulnerability)
    try:
        result = os.popen(command).read()
        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the application
if __name__ == "__main__":
    # Weak server configuration
    app.run(host="0.0.0.0", port=5000)

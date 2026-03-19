# user-microservice/app.py (MYSQL VERSION)

from flask import Flask, request, jsonify, render_template, redirect
import hashlib
import mysql.connector

app = Flask(__name__)

db_config = {
    "host": "user-db",
    "user": "user",
    "password": "userpass",
    "database": "usersdb"
}

def get_conn():
    return mysql.connector.connect(**db_config)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE,
            password VARCHAR(255)
        )
    ''')
    conn.commit()
    conn.close()

init_db()


# -------- REGISTER --------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")

    username = request.form.get('username')
    password = hash_password(request.form.get('password'))

    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        conn.close()
        return redirect('/login')
    except:
        return "User already exists"


# -------- LOGIN --------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    username = request.form.get('username')
    password = hash_password(request.form.get('password'))

    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return redirect(f"/login-success?username={username}")
    return "Invalid credentials"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5006)

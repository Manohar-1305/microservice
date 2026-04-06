import os
import re
import string
import secrets
from urllib.parse import urlparse

import pymysql
from flask import Flask, request, jsonify, redirect, render_template

PORT = 50007

# ---------- MySQL CONFIG ----------
DB_HOST = os.getenv("DB_HOST", "user-db")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "userpass")
DB_NAME = os.getenv("DB_NAME", "usersdb")

app = Flask(__name__)

# ---------- DB ----------
def get_db():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )


def init_db():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS short_urls (
                id INT AUTO_INCREMENT PRIMARY KEY,
                code VARCHAR(10) UNIQUE NOT NULL,
                long_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    db.commit()
    db.close()


# ---------- Helpers ----------
ALPHABET = string.ascii_letters + string.digits

def generate_code(length=7):
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def is_valid_url(u: str) -> bool:
    if not u or len(u) > 2048:
        return False
    if re.search(r"\s", u):
        return False
    p = urlparse(u)
    return p.scheme in ("http", "https") and bool(p.netloc)


def base_url():
    proto = request.headers.get("X-Forwarded-Proto", request.scheme)
    host = request.headers.get("X-Forwarded-Host", request.host)
    return f"{proto}://{host}"


def insert_url(long_url: str) -> str:
    db = get_db()
    for _ in range(10):
        code = generate_code(7)
        try:
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO short_urls(code, long_url) VALUES (%s, %s)",
                    (code, long_url)
                )
            db.commit()
            db.close()
            return code
        except Exception:
            continue
    db.close()
    raise RuntimeError("Could not generate a unique code")


def lookup_long_url(code: str):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT long_url FROM short_urls WHERE code=%s",
            (code,)
        )
        row = cur.fetchone()
    db.close()
    return row["long_url"] if row else None


# ---------- Routes ----------
@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/shorten")
def shorten():
    data = request.get_json(silent=True) or {}
    long_url = (data.get("long_url") or "").strip()

    if not is_valid_url(long_url):
        return jsonify({"error": "Invalid URL. Must start with http:// or https://"}), 400

    code = insert_url(long_url)
    short_url = f"{base_url().rstrip('/')}/{code}"

    return jsonify({
        "code": code,
        "short_url": short_url,
        "long_url": long_url
    }), 201


@app.get("/<code>")
def go(code):
    long_url = lookup_long_url(code)
    if not long_url:
        return "Not Found", 404

    return redirect(long_url, code=302)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=PORT, debug=True)

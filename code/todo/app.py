import os
from datetime import datetime, date

import pymysql
from flask import Flask, render_template, request, redirect, url_for, abort

PORT = 50009

# ---------- DB CONFIG ----------
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
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )


def init_db():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                is_done BOOLEAN DEFAULT FALSE,
                created_at DATETIME NOT NULL,
                task_date DATE NOT NULL
            )
        """)
    db.commit()
    db.close()


def today_str():
    return date.today().strftime("%Y-%m-%d")


def fetch_task(task_id: int):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM tasks WHERE id=%s", (task_id,))
        row = cur.fetchone()
    db.close()
    return row


# ---------- ROUTES ----------

@app.get("/")
def index():
    db = get_db()

    with db.cursor() as cur:
        cur.execute("""
            SELECT task_date AS d, COUNT(*) AS c
            FROM tasks
            GROUP BY d
            ORDER BY d DESC
        """)
        dates = cur.fetchall()

    selected_date = (request.args.get("date") or "").strip()

    if not selected_date:
        selected_date = today_str()
        if dates:
            selected_date = dates[0]["d"]

    with db.cursor() as cur:
        cur.execute("""
            SELECT * FROM tasks
            WHERE task_date=%s
            ORDER BY is_done ASC, id DESC
        """, (selected_date,))
        tasks = cur.fetchall()

    db.close()

    return render_template(
        "index.html",
        dates=dates,
        tasks=tasks,
        selected_date=selected_date,
        today=today_str()
    )

@app.route('/static/<path:filename>')
def static_files(filename):
    from flask import send_from_directory
    return send_from_directory('static', filename
                               )
@app.post("/add")
def add_task():
    title = (request.form.get("title") or "").strip()
    task_date = (request.form.get("task_date") or "").strip() or today_str()

    if not title:
        return redirect(url_for("index", date=task_date))

    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO tasks(title, is_done, created_at, task_date) VALUES (%s, %s, %s, %s)",
            (title, 0, datetime.now(), task_date)
        )
    db.commit()
    db.close()

    return redirect(url_for("index", date=task_date))


@app.post("/toggle/<int:task_id>")
def toggle_task(task_id):
    t = fetch_task(task_id)
    if not t:
        abort(404)

    new_val = 0 if t["is_done"] else 1

    db = get_db()
    with db.cursor() as cur:
        cur.execute("UPDATE tasks SET is_done=%s WHERE id=%s", (new_val, task_id))
    db.commit()
    db.close()

    return redirect(url_for("index", date=t["task_date"]))


@app.post("/delete/<int:task_id>")
def delete_task(task_id):
    t = fetch_task(task_id)
    if not t:
        abort(404)

    db = get_db()
    with db.cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    db.commit()
    db.close()

    return redirect(url_for("index", date=t["task_date"]))


@app.get("/edit/<int:task_id>")
def edit_page(task_id):
    t = fetch_task(task_id)
    if not t:
        abort(404)

    return render_template("edit.html", task=t, selected_date=t["task_date"])


@app.post("/edit/<int:task_id>")
def edit_save(task_id):
    t = fetch_task(task_id)
    if not t:
        abort(404)

    title = (request.form.get("title") or "").strip()
    selected_date = (request.form.get("selected_date") or "").strip() or t["task_date"]

    if not title:
        return redirect(url_for("edit_page", task_id=task_id))

    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE tasks SET title=%s WHERE id=%s",
            (title, task_id)
        )
    db.commit()
    db.close()

    return redirect(url_for("index", date=selected_date))
# ---------- START ----------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=PORT, debug=True)

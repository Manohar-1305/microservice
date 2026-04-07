import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import app, today_str


# ---------- Fixtures ----------
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ---------- Pure logic ----------
def test_today_str():
    assert len(today_str()) == 10


# ---------- Routes (NO DB CALLS EXECUTED) ----------

def test_index(monkeypatch, client):
    # prevent DB usage
    monkeypatch.setattr("app.get_db", lambda: type("X", (), {
        "execute": lambda *a, **k: type("R", (), {
            "fetchall": lambda self: [],
            "fetchone": lambda self: None
        })()
    })())
    monkeypatch.setattr("app.render_template", lambda *a, **k: "OK")

    res = client.get("/")
    assert res.status_code == 200


def test_add_task(monkeypatch, client):
    monkeypatch.setattr("app.get_db", lambda: type("X", (), {
        "execute": lambda *a, **k: None,
        "commit": lambda self: None
    })())

    res = client.post("/add", data={"title": "task"})
    assert res.status_code == 302


def test_toggle_task(monkeypatch, client):
    monkeypatch.setattr("app.fetch_task", lambda x: {"is_done": 0, "task_date": "2026-01-01"})
    monkeypatch.setattr("app.get_db", lambda: type("X", (), {
        "execute": lambda *a, **k: None,
        "commit": lambda self: None
    })())

    res = client.post("/toggle/1")
    assert res.status_code == 302


def test_edit_page(monkeypatch, client):
    monkeypatch.setattr("app.fetch_task", lambda x: {"id": 1, "task_date": "2026-01-01"})
    monkeypatch.setattr("app.render_template", lambda *a, **k: "OK")

    res = client.get("/edit/1")
    assert res.status_code == 200


def test_edit_save(monkeypatch, client):
    monkeypatch.setattr("app.fetch_task", lambda x: {"task_date": "2026-01-01"})
    monkeypatch.setattr("app.get_db", lambda: type("X", (), {
        "execute": lambda *a, **k: None,
        "commit": lambda self: None
    })())

    res = client.post("/edit/1", data={"title": "updated"})
    assert res.status_code == 302


def test_delete(monkeypatch, client):
    monkeypatch.setattr("app.fetch_task", lambda x: {"task_date": "2026-01-01"})
    monkeypatch.setattr("app.get_db", lambda: type("X", (), {
        "execute": lambda *a, **k: None,
        "commit": lambda self: None
    })())

    res = client.post("/delete/1")
    assert res.status_code == 302
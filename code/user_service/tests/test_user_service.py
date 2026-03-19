# tests/test_user_service.py

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# -------- REGISTER GET --------
def test_register_get(client):
    res = client.get("/register")
    assert res.status_code == 200


# -------- REGISTER SUCCESS --------
@patch("app.get_conn")
def test_register_success(mock_conn, client):
    mock_cursor = MagicMock()
    mock_connection = MagicMock()

    mock_connection.cursor.return_value = mock_cursor
    mock_conn.return_value = mock_connection

    res = client.post("/register", data={"username": "u", "password": "p"})

    assert res.status_code == 302
    assert "/login" in res.location


# -------- REGISTER DUPLICATE --------
@patch("app.get_conn")
def test_register_duplicate(mock_conn, client):
    mock_cursor = MagicMock()
    mock_connection = MagicMock()

    mock_cursor.execute.side_effect = Exception("duplicate")
    mock_connection.cursor.return_value = mock_cursor
    mock_conn.return_value = mock_connection

    res = client.post("/register", data={"username": "u", "password": "p"})

    assert b"User already exists" in res.data


# -------- LOGIN GET --------
def test_login_get(client):
    res = client.get("/login")
    assert res.status_code == 200


# -------- LOGIN SUCCESS --------
@patch("app.get_conn")
def test_login_success(mock_conn, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("id", "u", "hashed")

    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_conn.return_value = mock_connection

    res = client.post("/login", data={"username": "u", "password": "p"})

    assert res.status_code == 302
    assert "login-success" in res.location


# -------- LOGIN FAIL --------
@patch("app.get_conn")
def test_login_fail(mock_conn, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None

    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_conn.return_value = mock_connection

    res = client.post("/login", data={"username": "u", "password": "wrong"})

    assert b"Invalid credentials" in res.data
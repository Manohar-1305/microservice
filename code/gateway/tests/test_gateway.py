# tests/test_gateway.py

import sys
import os
from io import BytesIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import pytest
from unittest.mock import patch


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# -------- LOGIN --------
@patch("app.requests.get")
def test_login_get(mock_get, client):
    mock_get.return_value.text = "<form></form>"
    res = client.get("/login")
    assert res.status_code == 200


@patch("app.requests.post")
def test_login_success(mock_post, client):
    mock_post.return_value.status_code = 302

    res = client.post("/login", data={"username": "test", "password": "test"})
    assert res.status_code == 302
    assert "/home" in res.location


@patch("app.requests.post")
def test_login_fail(mock_post, client):
    mock_post.return_value.status_code = 401

    res = client.post("/login", data={"username": "bad", "password": "bad"})
    assert res.status_code == 302
    assert "error" in res.location


# -------- REGISTER --------
@patch("app.requests.post")
def test_register_success(mock_post, client):
    mock_post.return_value.status_code = 302

    res = client.post("/register", data={"username": "u", "password": "p"})
    assert res.status_code == 302


@patch("app.requests.post")
def test_register_fail(mock_post, client):
    mock_post.return_value.status_code = 400

    res = client.post("/register", data={"username": "u", "password": "p"})
    assert b"User already exists" in res.data


# -------- AUTH --------
def test_home_requires_login(client):
    res = client.get("/home")
    assert res.status_code == 302
    assert "/login" in res.location


def test_home_with_session(client):
    with client.session_transaction() as sess:
        sess["user"] = "test"

    res = client.get("/home")
    assert res.status_code == 200


# -------- AUDIO --------
@patch("app.requests.get")
def test_audio_page(mock_get, client):
    mock_get.return_value.content = b"ok"
    mock_get.return_value.status_code = 200

    with client.session_transaction() as sess:
        sess["user"] = "test"

    res = client.get("/audio")
    assert res.status_code == 200


# -------- WORD TO PDF --------
@patch("app.requests.post")
def test_word_to_pdf_api(mock_post, client):
    mock_post.return_value.content = b"pdf"
    mock_post.return_value.status_code = 200
    mock_post.return_value.headers = {"Content-Type": "application/pdf"}

    with client.session_transaction() as sess:
        sess["user"] = "test"

    data = {
        "word_file": (BytesIO(b"data"), "file.docx")
    }

    res = client.post("/word-to-pdf/convert", data=data, content_type='multipart/form-data')
    assert res.status_code == 200


# -------- LOGOUT --------
def test_logout(client):
    with client.session_transaction() as sess:
        sess["user"] = "test"

    res = client.get("/logout")
    assert res.status_code == 302
    assert "/login" in res.location
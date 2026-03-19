# tests/test_music_service.py

import sys
import os
from io import BytesIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import pytest


@pytest.fixture
def client(tmp_path):
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = tmp_path

    with app.test_client() as client:
        yield client


# -------- HOME --------
def test_home(client):
    res = client.get("/")
    assert res.status_code == 200


# -------- UPLOAD SUCCESS --------
def test_upload_success(client):
    data = {
        "music": (BytesIO(b"dummy data"), "test.mp3")
    }

    res = client.post("/upload", data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    assert b"test.mp3" in res.data


# -------- UPLOAD FAIL --------
def test_upload_no_file(client):
    res = client.post("/upload", data={}, content_type='multipart/form-data')
    assert res.status_code == 400
    assert b"No file provided" in res.data


# -------- LIST FILES --------
def test_list_files(client):
    # create dummy file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], "song.mp3")
    with open(file_path, "wb") as f:
        f.write(b"data")

    res = client.get("/list")
    assert res.status_code == 200
    assert b"song.mp3" in res.data


# -------- SERVE FILE --------
def test_serve_music(client):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], "song.mp3")
    with open(file_path, "wb") as f:
        f.write(b"data")

    res = client.get("/music_files/song.mp3")
    assert res.status_code == 200
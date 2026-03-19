# tests/test_word_to_pdf_service.py

import sys
import os
from io import BytesIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def client(tmp_path):
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = tmp_path / "uploads"
    app.config['OUTPUT_FOLDER'] = tmp_path / "converted"

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    with app.test_client() as client:
        yield client


# -------- UI --------
def test_index(client):
    res = client.get("/")
    assert res.status_code == 200


# -------- NO FILE --------
def test_no_file(client):
    res = client.post("/pdf_converter", data={}, content_type='multipart/form-data')
    assert res.status_code == 200
    assert b"No file uploaded" in res.data


# -------- EMPTY FILENAME --------
def test_empty_filename(client):
    data = {
        "word_file": (BytesIO(b""), "")
    }
    res = client.post("/pdf_converter", data=data, content_type='multipart/form-data')
    assert b"No selected file" in res.data


# -------- INVALID FILE TYPE --------
def test_invalid_file(client):
    data = {
        "word_file": (BytesIO(b"data"), "file.txt")
    }
    res = client.post("/pdf_converter", data=data, content_type='multipart/form-data')
    assert b"Only DOCX allowed" in res.data


# -------- SUCCESS --------
@patch("app.subprocess.run")
def test_convert_success(mock_run, client):
    mock_run.return_value = MagicMock(returncode=0)

    # create fake output file
    output_file = os.path.join(app.config['OUTPUT_FOLDER'], "test.pdf")
    with open(output_file, "wb") as f:
        f.write(b"pdf")

    data = {
        "word_file": (BytesIO(b"data"), "test.docx")
    }

    res = client.post("/pdf_converter", data=data, content_type='multipart/form-data')

    assert b"success" in res.data


# -------- CONVERSION FAIL --------
@patch("app.subprocess.run")
def test_convert_fail(mock_run, client):
    mock_run.return_value = MagicMock(returncode=1, stderr="error")

    data = {
        "word_file": (BytesIO(b"data"), "test.docx")
    }

    res = client.post("/pdf_converter", data=data, content_type='multipart/form-data')

    assert b"error" in res.data


# -------- DOWNLOAD --------
def test_download(client):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], "file.pdf")
    with open(file_path, "wb") as f:
        f.write(b"pdf")

    res = client.get("/download/file.pdf")
    assert res.status_code == 200
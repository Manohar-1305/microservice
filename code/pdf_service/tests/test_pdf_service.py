# tests/test_pdf_service.py

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
    os.chdir(tmp_path)  # isolate temp files

    with app.test_client() as client:
        yield client


# -------- UI --------
def test_pdf_ui(client):
    res = client.get("/pdf_converter")
    assert res.status_code == 200


# -------- CONVERT SUCCESS --------
@patch("app.Converter")
def test_convert_success(mock_converter, client):
    mock_instance = MagicMock()
    mock_converter.return_value = mock_instance

    # simulate output file creation
    def fake_convert(output_path, start=0, end=None):
        with open(output_path, "wb") as f:
            f.write(b"docx data")

    mock_instance.convert.side_effect = fake_convert

    data = {
        "file": (BytesIO(b"pdf data"), "test.pdf")
    }

    res = client.post("/convert", data=data, content_type='multipart/form-data')

    assert res.status_code == 200
    assert b"docx data" in res.data


# -------- NO FILE --------
def test_convert_no_file(client):
    res = client.post("/convert", data={}, content_type='multipart/form-data')
    assert res.status_code == 400
    assert b"No file provided" in res.data


# -------- EMPTY FILENAME --------
def test_convert_empty_filename(client):
    data = {
        "file": (BytesIO(b""), "")
    }

    res = client.post("/convert", data=data, content_type='multipart/form-data')
    assert res.status_code == 400
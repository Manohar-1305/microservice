# tests/test_audio_service.py

import sys
import os
from io import BytesIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# -------- GET PAGE --------
def test_convert_page(client):
    res = client.get("/convert")
    assert res.status_code == 200


# -------- POST SUCCESS --------
@patch("app.gTTS")
def test_convert_success(mock_gtts, client):
    mock_tts = MagicMock()
    mock_gtts.return_value = mock_tts

    res = client.post("/convert", json={"text": "hello"})

    assert res.status_code == 200
    assert res.content_type == "audio/mpeg"


# -------- POST EMPTY TEXT --------
def test_convert_empty_text(client):
    res = client.post("/convert", json={"text": ""})

    assert res.status_code == 400
    assert b"Please enter some text" in res.data


# -------- POST NO JSON --------
def test_convert_no_json(client):
    res = client.post("/convert", json={})

    assert res.status_code == 400
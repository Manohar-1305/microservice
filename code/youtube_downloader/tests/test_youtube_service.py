# tests/test_youtube_service.py

import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import pytest


@pytest.fixture
def client(tmp_path):
    app.config['TESTING'] = True
    app.DOWNLOAD_DIR = tmp_path
    os.makedirs(app.DOWNLOAD_DIR, exist_ok=True)

    with app.test_client() as client:
        yield client


# -------- UI --------
def test_youtube_home(client):
    res = client.get("/youtube")
    assert res.status_code == 200


# -------- FETCH PLAYLIST SUCCESS --------
@patch("app.requests.get")
def test_fetch_playlist_success(mock_get, client):
    mock_get.return_value.json.return_value = {"title": "Test Video"}

    res = client.get("/fetch_playlist?url=http://test.com")

    assert res.status_code == 200
    assert b"Test Video" in res.data


# -------- FETCH PLAYLIST FAIL --------
def test_fetch_playlist_no_url(client):
    res = client.get("/fetch_playlist")
    assert res.status_code == 400


# -------- DOWNLOAD SUCCESS --------
@patch("app.send_file")
@patch("app.uuid.uuid4")
def test_download_success(mock_uuid, mock_send_file, client):
    mock_uuid.return_value = "1234"
    mock_send_file.return_value = MagicMock(status_code=200)

    # create fake output file
    file_path = os.path.join(app.DOWNLOAD_DIR, "1234.mp4")
    with open(file_path, "wb") as f:
        f.write(b"video")

    fake_yt = MagicMock()
    fake_yt.YoutubeDL.return_value.__enter__.return_value = MagicMock()

    with patch.dict(sys.modules, {"yt_dlp": fake_yt}):
        res = client.get("/download_best?url=http://test.com")

    assert res.status_code == 200


# -------- DOWNLOAD FAIL --------
def test_download_fail(client):
    fake_yt = MagicMock()
    fake_yt.YoutubeDL.side_effect = Exception("fail")

    with patch.dict(sys.modules, {"yt_dlp": fake_yt}):
        res = client.get("/download_best?url=http://test.com")

    assert res.status_code == 500


# -------- DOWNLOAD NO URL --------
def test_download_no_url(client):
    res = client.get("/download_best")
    assert res.status_code == 400
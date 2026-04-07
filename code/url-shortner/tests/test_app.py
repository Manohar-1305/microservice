import sys
import os

# force project root into path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import app, is_valid_url


# ---------- Fixtures ----------
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ---------- Unit tests ----------
def test_valid_url():
    assert is_valid_url("https://google.com") is True


def test_invalid_url():
    assert is_valid_url("ftp://bad.com") is False
    assert is_valid_url("http://") is False
    assert is_valid_url("not-a-url") is False


# ---------- Route tests ----------
def test_shorten_success(monkeypatch, client):
    def mock_insert_url(url):
        return "abc1234"

    monkeypatch.setattr("app.insert_url", mock_insert_url)

    res = client.post("/api/shorten", json={"long_url": "https://google.com"})

    assert res.status_code == 201
    data = res.get_json()
    assert data["code"] == "abc1234"
    assert "short_url" in data


def test_shorten_invalid(client):
    res = client.post("/api/shorten", json={"long_url": "bad-url"})
    assert res.status_code == 400


def test_redirect_found(monkeypatch, client):
    def mock_lookup(code):
        return "https://google.com"

    monkeypatch.setattr("app.lookup_long_url", mock_lookup)

    res = client.get("/abc1234")
    assert res.status_code == 302
    assert "google.com" in res.location


def test_redirect_not_found(monkeypatch, client):
    monkeypatch.setattr("app.lookup_long_url", lambda x: None)

    res = client.get("/nope")
    assert res.status_code == 404
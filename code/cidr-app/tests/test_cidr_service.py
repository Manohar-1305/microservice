import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_page_loads(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"CIDR Calculator" in r.data


def test_valid_cidr_24(client):
    r = client.post("/", data={"cidr": "192.168.1.0/24"})
    assert r.status_code == 200
    assert b"192.168.1.0" in r.data
    assert b"192.168.1.255" in r.data


def test_invalid_cidr(client):
    r = client.post("/", data={"cidr": "invalid"})
    assert r.status_code == 200
    assert b"Invalid CIDR" in r.data
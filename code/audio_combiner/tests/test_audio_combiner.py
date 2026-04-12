import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app
from io import BytesIO
from pydub import AudioSegment


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def generate_test_audio(duration=1000):
    audio = AudioSegment.silent(duration=duration)
    buffer = BytesIO()
    audio.export(buffer, format="mp3")
    buffer.seek(0)
    return buffer


def test_index_page(client):
    response = client.get('/audio-combiner')
    assert response.status_code == 200


def test_combine_audio_success(client):
    audio1 = generate_test_audio()
    audio2 = generate_test_audio()

    data = {
        'audio': [
            (audio1, 'test1.mp3'),
            (audio2, 'test2.mp3')
        ]
    }

    response = client.post(
        '/audio-combiner/combine',
        data=data,
        content_type='multipart/form-data'
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'audio/mpeg'


def test_combine_single_file(client):
    audio = generate_test_audio()

    data = {
        'audio': (audio, 'test.mp3')
    }

    response = client.post(
        '/audio-combiner/combine',
        data=data,
        content_type='multipart/form-data'
    )

    assert response.status_code == 200


def test_combine_no_files(client):
    response = client.post('/audio-combiner/combine')

    assert response.status_code >= 400


def test_invalid_file_type(client):
    fake_file = BytesIO(b"not audio")

    data = {
        'audio': (fake_file, 'fake.txt')
    }

    # pydub will likely fail → your app may crash
    with pytest.raises(Exception):
        client.post(
            '/audio-combiner/combine',
            data=data,
            content_type='multipart/form-data'
        )
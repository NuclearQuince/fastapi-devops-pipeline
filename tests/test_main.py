# tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get('/')
    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']
    assert 'Hello' in response.text


def test_health_check():
    """Tests the /health endpoint for a successful response.
    and a known string in the page ("System Health")"""
    response = client.get('/health')
    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']
    assert 'System Health' in response.text


def test_stats():
    """Tests the /stats endpoint for a successful response.
    and a known string in the page ("Request Stats")"""
    response = client.get('/stats')
    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']
    assert 'Request Stats' in response.text

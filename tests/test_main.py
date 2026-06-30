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
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['app_status'] == 'ok'
    assert response.json()['db_status'] == 'connected'


def test_stats():
    response = client.get('/stats')
    assert response.status_code == 200
    data = response.json()
    assert 'total_requests' in data
    assert 'avg_response_time_ms' in data
    assert 'requests_by_endpoint' in data

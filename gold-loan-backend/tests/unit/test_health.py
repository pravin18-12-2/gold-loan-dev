from app.main import app
from fastapi.testclient import TestClient


def test_health():
    c = TestClient(app)
    r = c.get('/api/v1/system/health')
    assert r.status_code == 200

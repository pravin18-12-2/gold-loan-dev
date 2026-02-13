import uuid
from app.main import app
from fastapi.testclient import TestClient


def test_idempotent_appraiser_create():
    c = TestClient(app)
    key = str(uuid.uuid4())
    headers = {
        'Authorization': 'Bearer token',
        'X-Tenant-ID': 'tenant-1',
        'Idempotency-Key': key,
    }
    payload = {
        'name': 'Ravi',
        'email': f'ravi-{uuid.uuid4()}@bank.com',
        'phone': '9999999999',
        'branch_id': 'b1',
        'appraiser_code': f'APP-{uuid.uuid4()}',
        'face_image_id': 'img1',
    }
    r1 = c.post('/api/v1/appraisers', json=payload, headers=headers)
    r2 = c.post('/api/v1/appraisers', json=payload, headers=headers)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()['data']['appraiser_id'] == r2.json()['data']['appraiser_id']

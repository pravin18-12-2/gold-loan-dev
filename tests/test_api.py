import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def headers(idem=True):
    h = {
        "Authorization": "Bearer token",
        "X-Tenant-ID": "tenant-1",
        "Content-Type": "application/json",
    }
    if idem:
        h["Idempotency-Key"] = str(uuid.uuid4())
    return h


def test_end_to_end_and_immutability():
    r = client.post(
        "/api/v1/appraisers",
        headers=headers(),
        json={
            "name": "Ravi Kumar",
            "email": "ravi@bank.com",
            "phone": "9876543210",
            "branch_id": "b1",
            "appraiser_code": "APP001",
            "face_image_id": "img-a",
        },
    )
    assert r.status_code == 201
    appraiser_id = r.json()["data"]["appraiser_id"]

    r = client.post(
        "/api/v1/customers",
        headers=headers(),
        json={"customer_code": "CUST001", "name": "Suresh", "face_image_id": "img-c"},
    )
    assert r.status_code == 201
    customer_id = r.json()["data"]["customer_id"]

    r = client.post(
        "/api/v1/loans",
        headers=headers(),
        json={
            "customer_id": customer_id,
            "appraiser_id": appraiser_id,
            "bank_id": "bank-1",
            "branch_id": "branch-1",
        },
    )
    assert r.status_code == 201
    loan_id = r.json()["data"]["loan_id"]

    r = client.post(
        f"/api/v1/loans/{loan_id}/compliance",
        headers=headers(),
        json={
            "total_jewel_count": 1,
            "overall_image_id": "img-overall",
            "jewel_images": [{"index": 1, "image_id": "img-j1"}],
        },
    )
    assert r.status_code == 200

    r = client.post(f"/api/v1/loans/{loan_id}/purity-test", headers=headers(), json={})
    assert r.status_code == 200

    r = client.post(f"/api/v1/loans/{loan_id}/complete", headers=headers(), json={})
    assert r.status_code == 200

    r = client.post(
        f"/api/v1/loans/{loan_id}/compliance",
        headers=headers(),
        json={
            "total_jewel_count": 1,
            "overall_image_id": "img-overall",
            "jewel_images": [{"index": 1, "image_id": "img-j1"}],
        },
    )
    assert r.status_code == 403


def test_idempotency_same_request_same_response():
    idem = str(uuid.uuid4())
    payload = {
        "name": "Ravi Kumar 2",
        "email": "ravi2@bank.com",
        "phone": "9876543211",
        "branch_id": "b1",
        "appraiser_code": f"APP-{uuid.uuid4()}",
        "face_image_id": "img-a",
    }
    h = headers()
    h["Idempotency-Key"] = idem
    r1 = client.post("/api/v1/appraisers", headers=h, json=payload)
    assert r1.status_code == 201
    r2 = client.post("/api/v1/appraisers", headers=h, json=payload)
    assert r2.status_code == 201
    assert r1.json()["data"]["appraiser_id"] == r2.json()["data"]["appraiser_id"]

# Gold Loan Production Backend (FastAPI)

Production-style backend implementation for the v1 Gold Loan API with:
- tenant-aware API enforcement (`X-Tenant-ID`)
- JWT bearer header enforcement
- idempotency support for critical POST APIs
- immutable loan lifecycle (`COMPLETED` locks compliance/purity)
- audit logging and standardized response envelopes

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test
```bash
pytest -q
```

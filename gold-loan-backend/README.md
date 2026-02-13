# gold-loan-backend

Production-oriented FastAPI backend using **Supabase Postgres only**.

## Structure
Implements layered architecture: config, core, models, schemas, repositories, services, api, integrations, workers, tests, docker.

## Run
```bash
cd gold-loan-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment
Set only Supabase DB connection:
- `SUPABASE_DB_URL`
- `JWT_SECRET`

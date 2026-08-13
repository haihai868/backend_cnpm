# backend_cnpm

This repository contains a FastAPI backend application. The project has been
reorganized to follow a simple layered architecture: controllers (API routers),
services (business logic), and repositories (data access). Existing router
behaviour is preserved to keep API responses unchanged.

Quick start

- Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Unix/macOS
source .venv/bin/activate
```

- Install dependencies:

```bash
pip install -r requirements.txt
```

- Run the app with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Project layout

- `app/controllers` — API router exports (controllers/adapters).
- `app/services` — Business logic (move code here from routers over time).
- `app/repositories` — Data access / DB operations.
- `app/models` — ORM models (SQLAlchemy).
- `app/schemas` — Pydantic schemas.
- `app/routers` — Existing routers (kept for now to preserve behaviour).

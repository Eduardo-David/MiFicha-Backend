# TASK-A001: Backend Bootstrap with FastAPI, Docker y Python venv/pip

## 1. Task Metadata
- **Task ID:** A-001
- **Feature Traceability:** SYSTEM-BOOTSTRAP (Foundational Layer)
- **Role Constraint:** Expert Backend Software Engineer
- **Priority:** P0 (Blocker)
- **Status:** Pending
- **Created:** 2026-09-06

---

## 2. Goal & Context
The goal of this task is to initialize the boilerplate workspace for the **MiFicha** backend. You will establish a clean, production-ready, and testable project structure utilizing **FastAPI**, manage dependencies cleanly using Python virtual environments (venv) and pip with a requirements.txt file, centralize configuration with **Pydantic Settings**, and containerize the environment using **Docker** and **Docker Compose** to run FastAPI alongside a **PostgreSQL 16** database.

This skeleton is the architectural foundation. It is critical that this structure is sound, robust, and correctly isolated before any domain-specific entities or migrations are introduced.

---

## 3. Directory Layout Blueprint
You are strictly required to organize the files according to the Hexagonal Architecture/Ports & Adapters layout specified in `/agent/AGENT.md`. For this bootstrapping task, establish the following files and directories:

```text
/
├── requirements.txt            # pip dependency definition file
├── Dockerfile                  # Multi-stage production/development Dockerfile
├── docker-compose.yml          # Container orchestration (FastAPI + PostgreSQL)
├── .env.example                # Example template for environment variables
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI Application Initialization
│   └── core/
│       ├── __init__.py
│       └── config.py           # Pydantic Settings implementation
└── tests/
    ├── __init__.py
    ├── conftest.py             # Pytest configuration and client fixtures
    └── test_health.py          # Basic health check test case
```

---

## 4. Allowed & Forbidden Boundaries

### Allowed Files (Write Access)
You are permitted to **create** and **modify** ONLY the following files:
- `requirements.txt`
- `/poetry.lock`
- `/Dockerfile`
- `/docker-compose.yml`
- `/.env.example`
- `/src/main.py`
- `/src/core/config.py`
- `/tests/conftest.py`
- `/tests/test_health.py`

### Forbidden Boundaries (Strictly Blocked)
- **DO NOT** modify, delete, or write inside `/docs/` or `/agent/` directories.
- **DO NOT** modify `/tasks/task-index.md` directly.
- **DO NOT** create any SQLModel or SQLAlchemy models for domains (e.g., Accounts, Users) yet. That belongs to Task `A-002`.
- **DO NOT** initialize Alembic or generate migration scripts yet. That belongs to Task `A-002`.
- **DO NOT** import external HTTP clients or write any OCR-related logic. That belongs to Task `A-005`.

---

## 5. Technical Specifications

### A. Dependencies (requirements.txt + venv)
Create a virtual environment for Python ^3.12 and list dependencies in `requirements.txt`. Include the following packages:
- `fastapi` (>=0.110.0)
- `uvicorn[standard]` (>=0.28.0)
- `pydantic-settings` (>=2.2.0)
- `sqlmodel` (>=0.0.16)  *Installed as a dependency, but unused in code for this task*
- `alembic` (>=1.13.0)   *Installed as a dependency, but unused in code for this task*
- `psycopg2-binary` (>=2.9.0)
- `bcrypt` (>=4.1.0)

**Development Dependencies:**
- `pytest` (>=8.0.0)
- `httpx` (>=0.27.0)

### B. Environment Configuration (`src/core/config.py`)
Implement environment configuration loading using **Pydantic Settings**. Define a subclass of `BaseSettings` named `Settings`:
- **Attributes:**
  - `PROJECT_NAME`: `str` (Default: `"MiFicha Backend"`)
  - `API_V1_STR`: `str` (Default: `"/api/v1"`)
  - `POSTGRES_SERVER`: `str` (Required)
  - `POSTGRES_USER`: `str` (Required)
  - `POSTGRES_PASSWORD`: `str` (Required)
  - `POSTGRES_DB`: `str` (Required)
  - `DATABASE_URL`: `str` (A computed property or model-validator that builds the PostgreSQL DSN in the format: `postgresql://{user}:{password}@{server}/{db}`)
- Enforce loading variables from a local `.env` file if present, but prioritize actual environment variables.

### C. Application Entrypoint (`src/main.py`)
- Initialize the `FastAPI` instance using settings loaded from `src.core.config`.
- Set up a single router under the prefix `/api/v1`.
- Implement a **Health Check Endpoint**:
  - **Method:** `GET`
  - **Route:** `/api/v1/health`
  - **Expected Response JSON:** `{"status": "ok", "project": "MiFicha Backend"}`
  - **Status Code:** `200 OK`

### D. Dockerization
- **Dockerfile:** Create a clean, multi-stage or optimized single-stage build using a lightweight Python 3.12 image.
  - Create a virtual environment, copy only `requirements.txt`, and install dependencies with pip install -r `requirements.txt` in the final stage.
  - Set the default command to run Uvicorn pointing to `src.main:app` on port `8000`.
- **docker-compose.yml:** Define two services:
  1. `web`: Builds the `Dockerfile`. Mounts local files for development. Binds port `8000:8000`. Depends on the `db` service. Maps env vars using a `.env` file.
  2. `db`: Uses standard `postgres:16-alpine`. Configures the PostgreSQL database, user, password, and maps port `5432:5432`. Mounts a persistent volume for DB data. Includes a PG-healthcheck to ensure the backend only starts when PostgreSQL is ready to accept connections.

---

## 6. Expected Tests (`/tests/`)
Your work must pass a basic automated test suite implemented in **Pytest**.
- **`tests/conftest.py`:** Define a fixture named `client` that yields a Starlette/FastAPI `TestClient` initialized with the application app instance from `src.main.app`.
- **`tests/test_health.py`:** 
  - Create a test function named `test_health_endpoint_returns_ok`.
  - It must perform a `GET` request using the `client` fixture to `/api/v1/health`.
  - It must assert that the HTTP status code is `200 OK`.
  - It must assert that the payload matches `{"status": "ok", "project": "MiFicha Backend"}` exactly.

---

## 7. Out of Scope
- Creating SQLAlchemy or SQLModel engine initialization classes, database helper modules, or tables.
- Configuring database sessions or repositories.
- Handling authentication, JWT signing, or user creation.

---

## 8. Definition of Done (Done Criteria)
The task is successfully completed ONLY when:
1. Docker Compose can spin up both services (`docker compose up --build`) without errors, and the containers pass their internal healthchecks.
2. The Pytest test suite is executed within the `web` container (or local environment mimicking it) and passes with 100% success.
3. The codebase is clean, conforms strictly to PEP 8, and has no hardcoded secrets or database URLs.
4. All written logs and code comments are strictly in **English**.

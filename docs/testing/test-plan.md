# Test Plan - MiFicha Backend
**Project Name:** MiFicha Backend
**Tech Stack:** Python 3.12, FastAPI, PostgreSQL, SQLModel/SQLAlchemy
**Testing Framework:** Pytest

---

## 1. Test Philosophy & Strategy
In accordance with *Spec-Driven AI Engineering*, testing is our primary quality gate. Correct behavior and failure paths must be defined before code implementation. AI agents are prohibited from submitting any task without verifying that the associated test cases pass with 100% success.

Our goal is not generic coverage, but deterministic proof that every business requirement and security constraint is verified.

---

## 2. Directory Layout & Test Levels
The project organizes the `/tests` folder into distinct isolation boundaries matching our Hexagonal (Ports & Adapters) + DDD architecture:

```text
/tests
├── unit/             # 100% Isolated Domain & Pure Business Logic Tests (mocks all ports/repositories)
├── integration/      # Ports, Adapters, FastAPI Routes, PostgreSQL Repositories (ephemeral Postgres in Docker)
└── failure/          # Negative cases, error boundaries, security-sensitive rejections, data-leak prevention
```

### 2.1 Unit Tests (`/tests/unit`)
*   **Focus:** Core Domain Entities (e.g., `Cuenta`, `Persona`) and pure Python calculations.
*   **Isolation Policy:** Strictly prohibited from importing database engines, calling actual networks, or invoking external cryptographic adapters. All interfaces (ports) must be represented as mocks (e.g., mocking `IPasswordHasher`, `ICuentaRepository`).

### 2.2 Integration Tests (`/tests/integration`)
*   **Focus:** FastAPI endpoint routing, DB entity mapping, transaction management, and coordinate layer (`AdministrarCuentaService`).
*   **Infrastructure Requirement:** These tests MUST run against a live PostgreSQL instance running inside a Docker container to prevent dialect drift (avoid SQLite for JSONB or UUID compatibility reasons).
*   **Mocking Boundaries:** Third-party APIs (such as OCR document readers) must be mocked using their adapter interfaces (e.g., `IOCRService`) to ensure deterministic and cost-free test executions.

### 2.3 Failure & Security Tests (`/tests/failure`)
*   **Focus:** Denial paths, token expiration, validation errors, and bad inputs.
*   **Constraint:** Ensure no Postgres internals or FastAPI stack traces leak to the response payload on failure (Safe Error Handling Policy).

---

## 3. Mocking & External Dependency Policies
1.  **PostgreSQL Isolation:** A clean PostgreSQL container must be initialized per test suite execution using pytest-docker fixtures. Data must be truncated between tests.
2.  **OCR Service Mocking:** Since processing carnet photos via OCR relies on cloud AI API endpoints, all tests in integration and unit suites must inject a mock `IOCRService` returning predictable metadata (or raising `OCRIlegibleException` for failure paths) to prevent network delays and API billing.

---

## 4. Requirement-to-Test Traceability Matrix (Module: Administrar Usuario)

Every test written must declare its traceability to business requirement IDs (from the PRD) using comments or Pytest marks (`@pytest.mark.trace('REQ-ID')`).

| Test ID | Related Requirement | Test Level | Test Scenario | Preconditions | Input Data | Expected Result | Failure Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TEST-USR-001** | REQ-USR-REG-01 | Integration | Account registration with valid details and OCR extraction. | Database empty, hardware ID unique. | Valid photo upload, ANDROID_ID = "device-1" | 201 Created. User account created, password hashed, hardware ID linked. | Registration mechanism fails to coordinate OCR or base persistence. |
| **TEST-USR-002** | REQ-USR-REG-01 | Failure | Registration blocked because Android ID is already active. | Account exists with ANDROID_ID = "device-1". | New registration request with ANDROID_ID = "device-1" | 400 Bad Request. "Device already registered to an active account." No record created. | Failure to prevent multi-account spamming on same physical device. |
| **TEST-USR-003** | REQ-USR-REG-01 | Failure | Registration fails due to unreadable OCR carnet photo. | Empty DB, valid Android ID. | Distorted photo, OCR service fails. | 422 Unprocessable Entity. "Document could not be processed." No database entity created. | System persists empty/corrupted personal details when OCR fails. |
| **TEST-USR-004** | REQ-USR-MOD-02 | Unit / Domain | Modify contact details (Success after 24 hours). | Cuenta exists with fechaUltimaModificacion = "2026-09-05T00:00:00Z". Current time = "2026-09-06T09:00:00Z" (33h elapsed). | New phone/email | State of Cuenta updated, fechaUltimaModificacion updated to current time. | Domain model blocks editing even when the temporal window allows it. |
| **TEST-USR-005** | REQ-USR-MOD-02 | Failure | Block modifications within the 24-hour limit. | Cuenta exists with fechaUltimaModificacion = "2026-09-06T00:00:00Z". Current time = "2026-09-06T12:00:00Z" (12h elapsed). | New phone/email | `RestriccionTiempoException` raised. Returns 400 Bad Request indicating exact hours remaining. | Violation of product lockouts; users can spam server changes. |
| **TEST-USR-006** | REQ-USR-DEL-03 | Integration | Delete Account (Success with credentials). | Cuenta exists with linked device-1 and Persona (Carnet = "123456"). | Correct password, idUsuario | 200 OK. Cuenta is logically removed/marked inactive, device relationship set to NULL, carnet freed. | Identifiers are locked permanently, preventing re-registration of the physical hardware/person. |
| **TEST-USR-007** | REQ-USR-DEL-03 | Failure | Rejection of account deletion due to invalid credentials. | Cuenta exists with hashed password. | Incorrect password | 401 Unauthorized. "Invalid credentials." Account and device associations remain unchanged. | Authorization flaw allowing unauthorized account destruction. |

---

## 5. Quality Gate & Hand-off Protocol (Agent Rules)
1.  **Run Tests Before Hand-off:** An AI agent must execute `pytest` in the terminal before declaring any task complete. No code changes will be merged if any unit, integration, or failure test fails.
2.  **No Dialect Bypass:** Tests MUST NOT bypass the repositories to directly insert records into Postgres. Always test through the clean `ICuentaRepository` port to ensure entity state mapping is audited.
3.  **Regression Locking:** When a bug is discovered, the developer or agent must first write a failing test under `/tests/failure/` to reproduce it. The bug is considered fixed only when that test turns green, and the test plan / AGENT.md is updated.

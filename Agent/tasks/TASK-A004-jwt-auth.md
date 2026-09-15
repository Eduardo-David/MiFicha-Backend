# Task Spec: TASK-A004 - Implement JWT Authentication Flow & Password Hashing

- **Task ID:** `A-004`
- **Feature Target:** User Authentication & Security Infrastructure
- **Traceability Link:** `REQ-AUTH-002` (in `/docs/requirements.md`), `task-index.md` (Task A-004)
- **Target Audience:** Autonomous AI Agent / Developer Team
- **Prerequisites:** Task `A-001` (Bootstrap), Task `A-002` (Database Schemas), Task `A-003` (Pure Domain Logic)

---

## 1. Context & Objective

The goal of this task is to implement a secure, production-ready user authentication flow using **JSON Web Tokens (JWT)** and **Bcrypt password hashing**, fully aligned with Hexagonal Architecture and Domain-Driven Design (DDD) principles. 

The application must expose a `POST /api/v1/auth/login` endpoint while strictly decoupling core application logic from third-party security libraries through abstract ports.

---

## 2. Allowed Workspace & Boundary Restrictions

### Permitted Modifications / Creations:
- `src/users/application/ports/token_service.py` (New Abstract Interface for Token Operations)
- `src/users/infrastructure/auth/bcrypt_hasher.py` (Adapter implementing `IPasswordHasher` from domain)
- `src/users/infrastructure/auth/jwt_service.py` (Adapter implementing `ITokenService`)
- `src/users/application/login_use_case.py` (Application Use Case for Login)
- `src/users/infrastructure/api/routes.py` (FastAPI HTTP controller for `/auth/login`)
- `src/core/config.py` (Add cryptographic settings)
- `tests/integration/test_auth.py` (Integration tests for authentication)
- `tests/failure/test_auth_failures.py` (Security failure & timing-attack tests)

### Strictly Forbidden Boundaries:
- **DO NOT** modify any pure domain entity or port in `src/users/domain/` (defined in `A-003`).
- **DO NOT** modify Alembic migration files under `alembic/`.
- **DO NOT** hardcode secrets or fallback strings in source code.

---

## 3. Cryptographic & Security Requirements

### A. Secrets Management & Fail-Fast Startup
- Update `src/core/config.py` (Pydantic Settings) to include:
  - `JWT_SECRET_KEY: str = Field(...)` — Must **NOT** have a default value. If `JWT_SECRET_KEY` is missing from the environment (`.env`), the application must fail immediately on startup.
  - `ACCESS_TOKEN_EXPIRE_MINUTES: int = 15` — Token expiration lifetime.
  - `JWT_ALGORITHM: str = "HS256"` — Cryptographic signing algorithm.

### B. Password Hashing (`BcryptPasswordHasher`)
- Implement `BcryptPasswordHasher` under `src/users/infrastructure/auth/bcrypt_hasher.py` implementing the domain port `IPasswordHasher`.
- Must use `bcrypt` for password hashing and verification.

### C. Token Service Port & Adapter (`PyJWT`)
- Define abstract interface `ITokenService` in `src/users/application/ports/token_service.py`:
  - `create_access_token(data: dict) -> str`
  - `verify_token(token: str) -> dict`
- Implement `PyJWTTokenService` under `src/users/infrastructure/auth/jwt_service.py` using `PyJWT`.
- Token Payload Claims MUST contain:
  - `sub`: User ID as string (UUID).
  - `exp`: Expiration UNIX timestamp (`current_time + ACCESS_TOKEN_EXPIRE_MINUTES`).
  - **FORBIDDEN:** Do NOT embed passwords, hashes, or personal identifiable information (PII) inside the JWT token payload.

### D. Anti-Enumeration & Anti-Timing Attack Guardrails
1. **Unified Error Response:** Any authentication failure (whether the email does not exist in the DB or the password is incorrect) MUST return `HTTP 401 Unauthorized` with the generic body:
   `{"detail": "Incorrect email or password"}`
2. **Timing Attack Protection:** If an email is not found in PostgreSQL during a login attempt, the system MUST still execute a dummy `bcrypt.checkpw` check against a pre-calculated dummy hash before returning the `401` response. This guarantees constant execution time for all login attempts regardless of account existence.
3. **Zero Sensitive Logging:** Plaintext passwords, secrets, or full JWT tokens MUST NEVER be printed to standard output, system logs, or error responses.

---

## 4. API Specification & Schemas

### Endpoint: `POST /api/v1/auth/login`

#### Request Schema: `UserLoginRequest`
```python
from pydantic import BaseModel, EmailStr, Field

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
```

#### Success Response (`200 OK`): `TokenResponse`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Client Error Responses:
- `401 Unauthorized`: `{"detail": "Incorrect email or password"}`
- `422 Unprocessable Entity`: Pydantic validation failure (e.g., password < 8 characters or malformed email).

---

## 5. Acceptance Criteria (BDD / Gherkin)

```gherkin
Feature: User Authentication & JWT Token Issuance

  Scenario: Successful login with valid credentials
    Given a registered user with email "patient@mificha.com" and password "SecurePass123"
    When I send a POST request to "/api/v1/auth/login" with valid email and password
    Then the response status code should be 200
    And the response body should contain "access_token" and "token_type" equal to "bearer"
    And the token should be valid and expire in 15 minutes

  Scenario: Failed login with incorrect password
    Given a registered user with email "patient@mificha.com"
    When I send a POST request to "/api/v1/auth/login" with email "patient@mificha.com" and password "WrongPassword"
    Then the response status code should be 401
    And the response detail should be "Incorrect email or password"

  Scenario: Failed login with non-existent email (Anti-timing protection)
    Given no user exists with email "unknown@mificha.com"
    When I send a POST request to "/api/v1/auth/login" with email "unknown@mificha.com" and password "SecurePass123"
    Then a dummy password verification check is executed
    And the response status code should be 401
    And the response detail should be "Incorrect email or password"

  Scenario: Rejection of malformed input (Validation Gate)
    When I send a POST request to "/api/v1/auth/login" with password "short"
    Then the response status code should be 422
```

---

## 6. Required Developer Environment Reminder

The AI Agent MUST include the following notice in its conversational response to the developer upon completing the plan or implementation:

> ⚠️ **Developer Action Required:** Make sure to set `JWT_SECRET_KEY=<your-secure-secret-key>` in your local `.env` file before starting the Docker environment or running tests. If missing, Pydantic Settings will trigger a fail-fast startup error.

---

## 7. Quality Gate & Run Protocol

1. Run unit and integration tests inside Docker:
   ```bash
   docker compose exec backend pytest tests/integration/test_auth.py tests/failure/test_auth_failures.py
   ```
2. **Quality Rule:** The AI Agent is permitted a maximum of **THREE (3) attempts** to resolve any test failure or syntax error during execution.

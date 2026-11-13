# Task Index - MiFicha Backend Module: Administrar Usuario

This file acts as the single source of truth for the work backlog of the AI Agent on the current branch. Tasks A-001 through A-008 are consolidated in this branch to complete the full scope of UC0: Administrar Usuario.

## Task Matrix

| Task ID | Task Name / Goal | Priority | Dependencies | Expected Output (Success Criteria) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A-001** | Create project structure and core configurations | P0 | None | FastAPI application initialized with Ports & Adapters folder layout. PostgreSQL container running via Docker Compose. `/health` endpoint responding with 200 OK. | [x] Completed |
| **A-002** | Define database schemas with SQLModel & Alembic | P0 | A-001 | Database models for `Cuenta`, `Persona`, and `Dispositivo` mapped with correct constraints. Alembic migrations generated and applied successfully in PostgreSQL database. | [x] Completed |
| **A-003** | Implement rich domain models & domain logic | P0 | A-002 | Business logic embedded directly within `/domain` entities (e.g., 24-hour lock calculation, hardware device untying). Pytest suite in `/tests/unit` passing 100% in isolation. | [x] Completed |
| **A-004** | Implement JWT authentication flow & password hashing | P1 | A-003 | Secure login endpoint `/auth/login` implemented using Bcrypt hashing. JWT token emission and validation. Verification of failing credentials returning secure controlled errors. | [x] Completed |
| **A-005** | Create user account with OCR port and device binding | P1 | A-004 | `POST /api/v1/usuarios` creates `Persona`, `User` and `Device` atomically, hashes the password, rejects duplicate identity/email/Android ID values, and uses `IOCRService` through a deterministic test mock. | [x] Completed |
| **A-006** | Implement profile updates with 24-hour lock | P1 | A-005 | Endpoint `PUT /api/v1/usuarios/perfil` protected by JWT. Checks last modification timestamp via domain entity logic. Throws custom safe exception with remaining time if <24h. | [x] Completed |
| **A-007** | Implement account deletion & asset release | P1 | A-006 | Endpoint `DELETE /api/v1/usuarios/cuenta` protected by JWT. Requires cryptographically secure password challenge. Unties `ANDROID_ID` logically and deletes record, releasing Carnet de Identidad in DB. | [x] Completed |
| **A-008** | Execute Stage-Gate quality check & full-suite verification | P2 | A-007 | Entire Pytest suite (unit, integration, and failure test cases) passing successfully. Zero "spec drift" detected. | [x] Completed |

## Dependency Graph & Rules

1. **Foundations First:** Do not start on business logic (A-003, A-004) before database models (A-002) and project structures (A-001) are fully set up and verified.
2. **Registration Dependency:** A-005 depends on the completed database, domain, and authentication foundations (A-001 through A-004), but does not issue a JWT; clients use the existing login flow after registration.
3. **Atomic Registration:** Creating `Persona`, `User`, and `Device` must be one transaction. A failure in any step must not leave partial records.
4. **Domain Purity Guardrail:** A-005 defines the `IOCRService` port and implements only a deterministic mock adapter for testing. Real third-party OCR integration is out of scope.
5. **Authentication Protection:** A-006 and A-007 must be strictly protected with JWT authentication (`get_current_user` dependency).
6. **Domain Invariant Enforcement:** Profile modifications (A-006) must enforce the 24-hour lock calculated in domain entity logic. Account deletion (A-007) must verify credentials and cleanly unlink hardware and identity.

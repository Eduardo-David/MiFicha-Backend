# Task Index - MiFicha Backend Module: Administrar Usuario

This file acts as the single source of truth for the work backlog of the AI Agent on the current branch. Based on `PROPUESTA-ALCANCE-RAMA.md`, this branch is intentionally limited to Tasks A-001 through A-005. Later user-management flows will be tracked in dedicated branches.

## Task Matrix

| Task ID | Task Name / Goal | Priority | Dependencies | Expected Output (Success Criteria) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A-001** | Create project structure and core configurations | P0 | None | FastAPI application initialized with Ports & Adapters folder layout. PostgreSQL container running via Docker Compose. `/health` endpoint responding with 200 OK. | [x] Completed |
| **A-002** | Define database schemas with SQLModel & Alembic | P0 | A-001 | Database models for `Cuenta`, `Persona`, and `Dispositivo` mapped with correct constraints. Alembic migrations generated and applied successfully in PostgreSQL database. | [x] completed |
| **A-003** | Implement rich domain models & domain logic | P0 | A-002 | Business logic embedded directly within `/domain` entities (e.g., 24-hour lock calculation, hardware device untying). Pytest suite in `/tests/unit` passing 100% in isolation. | [x] completed |
| **A-004** | Implement JWT authentication flow & password hashing | P1 | A-003 | Secure login endpoint `/auth/login` implemented using Bcrypt hashing. JWT token emission and validation. Verification of failing credentials returning secure controlled errors. | [x] Completed |
| **A-005** | Create user account with OCR port and device binding | P1 | A-004 | `POST /api/v1/usuarios` creates `Persona`, `User` and `Device` atomically, hashes the password, rejects duplicate identity/email/Android ID values, and uses `IOCRService` through a deterministic test mock. | [ ] Pending |

## Dependency Graph & Rules

1. **Foundations First:** Do not start on business logic (A-003, A-004) before database models (A-002) and project structures (A-001) are fully set up and verified.
2. **Registration Dependency:** A-005 depends on the completed database, domain, and authentication foundations (A-001 through A-004), but does not issue a JWT; clients use the existing login flow after registration.
3. **Atomic Registration:** Creating `Persona`, `User`, and `Device` must be one transaction. A failure in any step must not leave partial records.
4. **Domain Purity Guardrail:** A-005 defines the `IOCRService` port and implements only a deterministic mock adapter for testing. Real third-party OCR integration is out of scope.
5. **Branch Boundary:** Profile editing and account deletion are not part of this branch; they will be implemented in dedicated feature branches. Full-suite verification remains a pull-request quality policy, not a backlog task for this branch.

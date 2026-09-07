# Task Index - MiFicha Backend Module: Administrar Usuario

This file acts as the single source of truth for the work backlog of the AI Agent. Tasks must be executed in strict chronological order based on their priority and dependencies.

## Task Matrix

| Task ID | Task Name / Goal | Priority | Dependencies | Expected Output (Success Criteria) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A-001** | Create project structure and core configurations | P0 | None | FastAPI application initialized with Ports & Adapters folder layout. PostgreSQL container running via Docker Compose. `/health` endpoint responding with 200 OK. | [x] Completed |
| **A-002** | Define database schemas with SQLModel & Alembic | P0 | A-001 | Database models for `Cuenta`, `Persona`, and `Dispositivo` mapped with correct constraints. Alembic migrations generated and applied successfully in PostgreSQL database. | [x] completed |
| **A-003** | Implement rich domain models & domain logic | P0 | A-002 | Business logic embedded directly within `/domain` entities (e.g., 24-hour lock calculation, hardware device untying). Pytest suite in `/tests/unit` passing 100% in isolation. | [ ] Pending |
| **A-004** | Implement JWT authentication flow & password hashing | P1 | A-003 | Secure login endpoint `/auth/login` implemented using Bcrypt hashing. JWT token emission and validation. Verification of failing credentials returning secure controlled errors. | [ ] Pending |
| **A-005** | Implement account registration with OCR & device binding | P1 | A-004 | Endpoint `POST /api/v1/usuarios` fully operational. Integration with port `IOCRService` using a Pytest mock adapter. Ensures strict device binding rule (one active device per account). | [ ] Pending |
| **A-006** | Implement profile updates with 24-hour lock | P1 | A-005 | Endpoint `PUT /api/v1/usuarios/perfil` protected by JWT. Checks last modification timestamp via domain entity logic. Throws custom safe exception with remaining time if <24h. | [ ] Pending |
| **A-007** | Implement account deletion & asset release | P1 | A-006 | Endpoint `DELETE /api/v1/usuarios/cuenta` protected by JWT. Requires cryptographically secure password challenge. Unties `ANDROID_ID` logically and deletes record, releasing Carnet de Identidad in DB. | [ ] Pending |
| **A-008** | Execute Stage-Gate quality check & full-suite verification | P2 | A-007 | Entire Pytest suite (unit, integration, and failure test cases) passing successfully. Zero "spec drift" detected. | [ ] Pending |

## Dependency Graph & Rules

1. **Foundations First:** Do not start on business logic (A-003, A-004) before database models (A-002) and project structures (A-001) are fully set up and verified.
2. **Authentication Dependency:** Features requiring user identity (A-006, A-007) depend strictly on the completion of the JWT flow (A-004).
3. **Domain Purity Guardrail:** The OCR integration in A-005 must only define the domain port `IOCRService` and implement a mock adapter for testing. The real physical integration with third-party APIs must not be programmed in this task.

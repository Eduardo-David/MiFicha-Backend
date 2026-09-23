# Task Spec: TASK-A005 - Crear Cuenta de Usuario

- **Task ID:** `A-005`
- **Feature Target:** Registro de usuario, identidad y vinculación del dispositivo
- **Branch:** `feature/UC0-crear-cuenta-api`
- **Prerequisites:** Tasks `A-001` (Bootstrap), `A-002` (Database Schemas), `A-003` (Domain Logic), `A-004` (JWT Authentication)
- **Traceability:** `.agent/tasks/task-index.md`, `PROPUESTA-ALCANCE-RAMA.md`

## 1. Context and Objective

Implement the account-registration flow needed by the mobile client. The endpoint must create the related `Persona`, `User`, and `Device` records as one atomic operation, hash the password before persistence, and enforce that an email, identity card, and Android device identifier are not reused.

The branch ends after this task. Profile editing, account deletion, and full-suite stage-gate work are intentionally outside this task and will be handled in later branches or as pull-request quality checks.

## 2. Current Code Anchors

The implementation must build on the existing project instead of creating a parallel user flow:

| Area | Existing anchor | A-005 responsibility |
| --- | --- | --- |
| HTTP | `src/features/users/presentation/routes.py` | Add the registration route beside the existing auth route. |
| Persistence models | `src/features/users/data/models.py` | Persist `Persona`, `User`, and `Device` using the existing relationships and constraints. |
| Domain | `src/features/users/domain/models.py` | Reuse domain validation and entity creation rules. |
| Passwords | `src/features/users/data/auth/bcrypt_hasher.py` | Hash plaintext passwords through `IPasswordHasher`; never persist plaintext. |
| Repositories | `src/features/users/domain/ports.py` and `src/features/users/data/repositories.py` | Add or complete the ports/adapters needed to save the three related entities and check uniqueness. |

## 3. Allowed Scope

### Required

- Add `POST /api/v1/usuarios`.
- Define request and success response schemas with Pydantic.
- Create the `Persona`, `User` with role `patient`, and one `Device` linked to the new user.
- Validate required identity, contact, birth-date, credential, and device fields.
- Hash the password with the existing password-hasher port before saving it.
- Enforce uniqueness for `identity_card`, `email`, and `android_id` before or during the transaction.
- Roll back the complete registration if any related record cannot be saved.
- Define the domain/application port `IOCRService` and use it from the registration use case.
- Provide a deterministic mock OCR adapter for tests. The mock must return controlled identity data and must not call a real provider.
- Add unit and integration tests for the happy path, validation, uniqueness, transaction failure, password hashing, and device binding.

### Forbidden or Deferred

- Do not integrate a real OCR vendor, upload to an external service, or add API credentials.
- Do not implement profile updates or the 24-hour profile lock endpoint.
- Do not implement account deletion, password challenge, or asset release.
- Do not change JWT issuance or login behavior except where shared dependency wiring is required.
- Do not modify completed migration history unless a schema change is proven necessary and explicitly reviewed.

## 4. API Contract

### Endpoint

`POST /api/v1/usuarios`

### Request body

The request must contain the data required by the existing `Persona`, `User`, and `Device` models:

```json
{
  "first_name": "Laura",
  "last_name": "Pérez",
  "identity_card": "V-87654321-0",
  "birth_date": "1992-11-08",
  "phone": "71234567",
  "email": "laura.perez@example.com",
  "password": "SecurePass123",
  "android_id": "android-device-001"
}
```

Validation must reject malformed email, passwords shorter than 8 characters, invalid identity data, invalid phone data according to the domain rules, missing `birth_date`, and empty `android_id` with `422 Unprocessable Entity`.

### Success response

Return `201 Created` without returning the password or password hash:

```json
{
  "id": "<user-uuid>",
  "email": "laura.perez@example.com",
  "role": "patient"
}
```

The registration endpoint does not issue a JWT. The client can authenticate through the existing `POST /api/v1/auth/login` flow after registration succeeds.

### Conflict response

Return `409 Conflict` with a safe, field-oriented message when the email, identity card, or Android ID is already registered. Do not expose SQL exceptions, password data, or internal stack traces.

## 5. Registration Flow

1. Validate the HTTP request and normalize values where the existing domain contract permits it.
2. Ask `IOCRService` to validate or extract the identity data required by the registration use case. The initial adapter is a mock only.
3. Check whether the identity card, email, or Android ID is already associated with an account.
4. Build a `Persona`, a `User` with role `patient`, and a `Device` with the generated user ID.
5. Hash the password using `IPasswordHasher`.
6. Persist all three entities in one transaction, preserving foreign-key order.
7. Return the public registration response only after the transaction commits.

The application layer owns orchestration and business errors. The persistence adapter owns SQLModel/SQLAlchemy details. A database uniqueness violation must be translated into the same safe `409 Conflict` contract and must leave no partial registration behind.

## 6. Acceptance Criteria

```gherkin
Feature: User account registration

  Scenario: Register a patient with a device
    Given no account exists for the email, identity card, or Android ID
    When I POST valid registration data to "/api/v1/usuarios"
    Then the response status is 201
    And the response contains the new user id, email, and role "patient"
    And one Persona, one User, and one Device are persisted
    And the stored password is a bcrypt hash and is not the plaintext password

  Scenario: Reject a duplicated registration identity
    Given an account already uses the email, identity card, or Android ID
    When I POST registration data reusing that value
    Then the response status is 409
    And no additional Persona, User, or Device is created

  Scenario: Reject invalid registration data
    When I POST data with an invalid email, short password, invalid identity data,
    missing birth date, or empty Android ID
    Then the response status is 422

  Scenario: Use the OCR port without a real provider
    Given the registration use case receives the mock IOCRService adapter
    When I submit valid identity data
    Then the use case uses the port result
    And no external OCR API is called

  Scenario: Roll back a failed registration
    Given persistence fails while saving one of the related records
    When registration is executed
    Then the operation returns a controlled error
    And no partial Persona, User, or Device remains
```

## 7. Test Plan and Quality Gate

Add focused tests under the existing test layout:

- Unit tests for the registration use case with in-memory repositories, a fake password hasher, and the mock OCR adapter.
- Integration tests for `POST /api/v1/usuarios` against the configured database and Alembic schema.
- Failure tests for duplicate email, duplicate identity card, duplicate Android ID, malformed input, and rollback behavior.
- Regression checks confirming that the existing authentication tests still pass and that the stored password cannot be used as plaintext.

Run the focused registration tests first, then the existing suite:

```bash
pytest tests/unit tests/integration tests/failure
```

The task is complete when the focused and existing tests pass, the endpoint contract is documented by tests, and no real OCR integration or A-006/A-007 functionality has been added.

## 8. Completion Checklist

- [ ] Registration use case and route implemented at `POST /api/v1/usuarios`.
- [ ] `IOCRService` port and deterministic mock adapter added.
- [ ] Persona, User, and Device are persisted atomically.
- [ ] Password hashing and uniqueness conflicts are covered.
- [ ] Focused unit, integration, and failure tests pass.
- [ ] Existing authentication tests remain green.
- [ ] Scope remains limited to A-005.
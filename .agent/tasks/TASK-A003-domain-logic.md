# TASK-A003: Implement Rich Domain Models & Domain Logic

## 1. Context & Core Goal
The objective of this task is to establish the pure business logic and representation of the User Management system under the principles of **Domain-Driven Design (DDD)** and Craig Larman's **GRASP patterns** (specifically **Information Expert**). 

Following the strict rules established in `/agent/AGENT.md`, the domain layer must contain **zero external dependencies** (no frameworks, no databases, and no ORM metadata). All business validation rules and state transitions (such as the 24-hour profile modification lock) must be evaluated purely in memory within the domain models.

---

## 2. Target File Layout
The agent must implement the following layout inside the `src/users/domain/` directory:
```text
src/
└── users/
    └── domain/
        ├── __init__.py
        ├── models.py         # Pure domain entities (Persona, User, Device)
        ├── ports.py          # Abstract interfaces/ports (Repositories, Hashing)
        └── exceptions.py     # Strongly-typed domain exceptions
```

---

## 3. Strict Boundary Rules
*   **Zero Framework Imports:** You are strictly forbidden from importing `SQLModel`, `SQLAlchemy`, `Pydantic`, `FastAPI`, or any other network/database-related library inside `/src/users/domain/`.
*   **Pure Python Standard Libraries:** You may only use pure Python standard libraries (e.g., `uuid`, `datetime`, `abc`, `re`, `dataclasses`).
*   **No Infrastructure Intrusion:** Any conversion from these pure domain models to SQLModel physical schemas must occur strictly in the Infrastructure layer (via mappers), which will be designed in later tasks.

---

## 4. Technical Specifications & Class Contracts

### A. `src/users/domain/exceptions.py`
Define the core domain exception hierarchy:
*   `DomainException(Exception)`: Base exception for all domain errors.
*   `ValidationError(DomainException)`: Raised when constructors or inputs fail domain constraints.
*   `RestriccionTiempoException(DomainException)`: Raised when a profile update is requested before the 24-hour cooldown expires.
    *   *Attribute:* `time_remaining: timedelta` (The exact duration the user must wait).

### B. `src/users/domain/models.py`
Implement the following pure entities. You may use standard Python `@dataclass(slots=True)` or standard classes:

#### 1. `Persona`
Represents the physical identity of a human.
*   **Attributes:**
    *   `id: uuid.UUID`
    *   `first_name: str`
    *   `last_name: str`
    *   `identity_card: str` (Must support alphanumeric extensions, e.g., "1234567-1B")
    *   `email: str`
    *   `phone: str` (Bolivian phone format validation)
*   **Constructor Validations:**
    *   `identity_card` must be a non-empty string, alphanumeric (allowing one optional hyphen followed by alphanumeric characters for extensions), and must be at least 5 characters in length. If invalid, raise `ValidationError`.
    *   `email` must match a strict RFC-compliant email regex pattern (must contain `@` and a valid domain with a dot). If invalid, raise `ValidationError`.
    *   `phone` must be a valid Bolivian number: must start strictly with `6` or `7`, contain only digits, and have an exact length of 8 characters. If invalid, raise `ValidationError`.

#### 2. `User` (The Security/Account entity)
Represents the system credentials, security state, and access permissions.
*   **Attributes:**
    *   `id: uuid.UUID`
    *   `persona_id: uuid.UUID`
    *   `email: str`
    *   `password_hash: str`
    *   `role: str` (Must be one of: `"dev"`, `"admin"`, `"doctor"`, `"patient"`)
    *   `last_profile_update: datetime.datetime` (UTC timestamp)
*   **Behavior (Information Expert):**
    *   `update_profile(self, new_email: str, current_time: datetime.datetime) -> None`:
        *   **24-Hour Cooldown Validation:** Calculate the difference between `current_time` (which must be timezone-naive UTC) and `self.last_profile_update`. 
        *   If `current_time - self.last_profile_update` is less than `datetime.timedelta(hours=24)`:
            *   Calculate the remaining wait time.
            *   Raise `RestriccionTiempoException(time_remaining=remaining_time)` with a clear message: `"Profile modification is locked. Please wait {hours}h {minutes}m remaining."`
        *   If the validation passes:
            *   Update `self.email = new_email`.
            *   Update `self.last_profile_update = current_time`.

#### 3. `Device`
Represents a physical mobile terminal bound to a user account.
*   **Attributes:**
    *   `id: uuid.UUID`
    *   `user_id: uuid.UUID`
    *   `android_id: str` (The unique secure hardware identifier of the Android device)

### C. `src/users/domain/ports.py`
Define the logical boundaries (Ports) that infrastructure adapters must implement.

#### 1. `IPasswordHasher(abc.ABC)`
*   `hash(self, password: str) -> str`: Abstract method.
*   `verify(self, password: str, hashed: str) -> bool`: Abstract method.

#### 2. `IUserRepository(abc.ABC)`
*   `save(self, user: User) -> None`: Abstract method.
*   `find_by_id(self, user_id: uuid.UUID) -> User | None`: Abstract method.
*   `find_by_email(self, email: str) -> User | None`: Abstract method.
*   `delete(self, user_id: uuid.UUID) -> None`: Abstract method.

#### 3. `IDeviceRepository(abc.ABC)`
*   `save(self, device: Device) -> None`: Abstract method.
*   `find_by_android_id(self, android_id: str) -> Device | None`: Abstract method.
*   `delete_by_user_id(self, user_id: uuid.UUID) -> None`: Abstract method.

---

## 5. Acceptance Criteria & Pytest Verification (Gherkin BDD format)
The agent must implement corresponding unit tests under `/tests/unit/test_domain.py`. These tests must mock timestamps and verify the domain logic in absolute isolation.

### Scenario 1: Successful initialization of Persona with Bolivian validations
*   **Given** a valid first name, last name, and an alphanumeric identity card `"6543210-2A"`
*   **And** a valid email address `"user@mificha.com.bo"`
*   **And** a valid Bolivian phone number `"71234567"`
*   **When** the `Persona` entity is instantiated
*   **Then** the entity should be created successfully without errors.

### Scenario 2: Validation rejection on invalid Bolivian phone format
*   **Given** a phone number that starts with `"8"` (invalid prefix) or has a length of 7 digits
*   **When** a `Persona` entity is instantiated
*   **Then** raise a `ValidationError` exception.

### Scenario 3: Validation rejection on invalid identity card format
*   **Given** an identity card that is empty or less than 5 characters long
*   **When** a `Persona` entity is instantiated
*   **Then** raise a `ValidationError` exception.

### Scenario 4: Profile modification blocked within the 24-hour lock period
*   **Given** a `User` entity whose `last_profile_update` was set to `2026-09-06 12:00:00`
*   **And** a profile update request is made at `2026-09-06 18:00:00` (only 6 hours elapsed)
*   **When** `user.update_profile(new_email="new@mificha.com", current_time=datetime(2026, 9, 6, 18, 0, 0))` is called
*   **Then** raise a `RestriccionTiempoException`
*   **And** the exception's `time_remaining` attribute must be exactly `18 hours`.

### Scenario 5: Profile modification allowed after the 24-hour lock period
*   **Given** a `User` entity whose `last_profile_update` was set to `2026-09-06 12:00:00`
*   **And** a profile update request is made at `2026-09-07 13:00:00` (25 hours elapsed)
*   **When** `user.update_profile(new_email="new@mificha.com", current_time=datetime(2026, 9, 7, 13, 0, 0))` is called
*   **Then** update the user's email to `"new@mificha.com"`
*   **And** set the user's `last_profile_update` to `2026-09-07 13:00:00`.

---

## 6. Agent Verification Gate
To complete this task successfully:
1.  Verify that no external packages (SQLAlchemy, SQLModel, Pydantic, etc.) are imported inside any file under `/src/users/domain/`.
2.  Run the newly designed unit test suite:
    ```bash
    pytest tests/unit/test_domain.py
    ```
3.  Ensure 100% of the unit tests pass successfully.

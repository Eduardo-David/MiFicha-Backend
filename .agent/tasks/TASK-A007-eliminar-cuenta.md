# Task Spec: TASK-A007 - Eliminar Cuenta y Liberar Recursos

- **Task ID:** `A-007`
- **Feature Target:** Baja definitiva de cuenta, verificación de contraseña y liberación de hardware/identidad
- **Branch:** `feature/UC0-crear-cuenta-api`
- **Prerequisites:** Tasks `A-001` a `A-006`
- **Traceability:** `.agent/tasks/task-index.md`, `docs/developer/Artefacto Administrar Usuario.md`

## 1. Context and Objective

Implement the account deletion flow (Flujo Alternativo 3-10b). An authenticated patient can request the permanent deletion of their account. For security, the system must challenge the user for their current password. Upon confirmation, the system removes or deactivates the account, freeing the associated `android_id` (hardware device) and identity card (`identity_card`) so they can be registered again if needed.

## 2. Allowed Scope

### Required
- Implement `DELETE /api/v1/usuarios/cuenta` protected by JWT bearer token.
- Require password challenge verification using `IPasswordHasher`.
- If password is incorrect, return `401 Unauthorized`.
- If password is correct, delete the `User`, associated `Device` records, and `Persona` within a transaction.
- Ensure the hardware identifier (`android_id`) and `identity_card` are released in the database.
- Add unit and integration tests.

### API Contract

### Endpoint
`DELETE /api/v1/usuarios/cuenta`
Header: `Authorization: Bearer <token>`

### Request Body
```json
{
  "password": "CurrentPassword123"
}
```

### Success Response `200 OK`
```json
{
  "message": "Cuenta eliminada exitosamente. Se ha desvinculado el dispositivo y liberado la identidad."
}
```


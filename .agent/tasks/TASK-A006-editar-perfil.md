# Task Spec: TASK-A006 - Actualizar Perfil de Usuario

- **Task ID:** `A-006`
- **Feature Target:** Modificación de datos de contacto con regla de 24 horas
- **Branch:** `feature/UC0-crear-cuenta-api`
- **Prerequisites:** Tasks `A-001` a `A-005`
- **Traceability:** `.agent/tasks/task-index.md`, `docs/developer/Artefacto Administrar Usuario.md`

## 1. Context and Objective

Implement the profile update flow for authenticated users (Flujo Alternativo 3-10a). A patient who is logged in can update their contact information (such as email or phone). The system must enforce that at least 24 hours have elapsed since the user's last profile update. If fewer than 24 hours have passed, the request must be rejected with the remaining time.

## 2. Allowed Scope

### Required
- Implement `PUT /api/v1/usuarios/perfil` protected by JWT bearer token.
- Require authentication dependency (`get_current_user`).
- Validate incoming email and phone format according to domain invariants.
- Check `last_profile_update` on the `User` domain entity using the existing domain method `user.update_profile(new_email)`.
- If blocked (< 24h), return `403 Forbidden` (or controlled business error) with the remaining time in hours/minutes.
- If allowed, persist changes and update `last_profile_update` to the current UTC timestamp.
- Add unit tests for use case and integration tests for the endpoint.

### Forbidden
- Do not allow changing `identity_card` (Carnet) or `android_id` (hardware ID) in this endpoint.
- Do not bypass the 24-hour restriction.

## 3. API Contract

### Endpoint
`PUT /api/v1/usuarios/perfil`
Header: `Authorization: Bearer <token>`

### Request Body
```json
{
  "email": "nuevo.correo@example.com",
  "phone": "71234567"
}
```

### Success Response `200 OK`
```json
{
  "message": "Perfil actualizado exitosamente",
  "email": "nuevo.correo@example.com",
  "phone": "71234567"
}
```

### Business Error `< 24 horas` `403 Forbidden`
```json
{
  "detail": "No puede modificar su información de perfil hasta que transcurran 24 horas desde la última modificación. Tiempo restante: 14h 23m."
}
```


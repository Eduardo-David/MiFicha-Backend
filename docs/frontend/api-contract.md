# MiFicha Backend - Contrato de API para Frontend

Este documento sirve como referencia para implementar el cliente frontend sin levantar PostgreSQL ni Docker. Distingue los endpoints disponibles actualmente de los endpoints definidos por la tarea A-005, que todavía están pendientes de implementación.

## Base URL

En desarrollo, la API usa:

```text
http://localhost:8000/api/v1
```

Todas las rutas de este documento se expresan relativas a esa base URL.

## Estado de los endpoints

| Método | Ruta | Estado | Uso |
| --- | --- | --- | --- |
| `GET` | `/health` | Disponible | Verificar que el backend responde. |
| `POST` | `/auth/login` | Disponible | Autenticar una cuenta existente y recibir un JWT. |
| `POST` | `/usuarios` | Disponible | Crear una cuenta, su identidad y su dispositivo. |
| `PUT` | `/usuarios/perfil` | Disponible | Modificar datos de contacto (email, teléfono) con restricción de 24 horas. |
| `DELETE` | `/usuarios/cuenta` | Disponible | Eliminar cuenta con challenge de contraseña y liberación de hardware/cédula. |

## 1. Health check

### Request

```http
GET /api/v1/health
```

No requiere body ni autenticación.

### Response `200 OK`

```json
{
  "status": "ok",
  "project": "MiFicha Backend"
}
```

## 2. Iniciar sesión

### Request

```http
POST /api/v1/auth/login
Content-Type: application/json
```

```json
{
  "email": "patient@mificha.com",
  "password": "SecurePass123"
}
```

### Campos

| Campo | Tipo | Requerido | Regla |
| --- | --- | --- | --- |
| `email` | `string` | Sí | Debe tener formato de correo válido. |
| `password` | `string` | Sí | Entre 8 y 128 caracteres. |

### Response `200 OK`

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

El frontend debe conservar el `access_token` y enviarlo en las rutas protegidas con:

```http
Authorization: Bearer <jwt>
```

### Errors

#### `401 Unauthorized`

Se devuelve el mismo mensaje cuando el correo no existe o la contraseña es incorrecta:

```json
{
  "detail": "Incorrect email or password"
}
```

El frontend no debe distinguir entre correo inexistente y contraseña incorrecta.

#### `422 Unprocessable Entity`

Ocurre cuando el body no cumple la validación, por ejemplo, un correo inválido o una contraseña menor de 8 caracteres. FastAPI devuelve una lista de errores de validación:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "short"
    }
  ]
}
```

El frontend debe usar `loc` para identificar el campo inválido y mostrar su propio mensaje de usuario.

## 3. Crear cuenta - A-005

> **Estado:** Implementado y disponible.

### Request

```http
POST /api/v1/usuarios
Content-Type: application/json
```

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

### Campos

| Campo | Tipo | Requerido | Regla |
| --- | --- | --- | --- |
| `first_name` | `string` | Sí | Nombre de la persona. |
| `last_name` | `string` | Sí | Apellido de la persona. |
| `identity_card` | `string` | Sí | Identificador válido según las reglas de dominio; no puede estar registrado previamente. |
| `birth_date` | `string` | Sí | Fecha en formato ISO `YYYY-MM-DD`. |
| `phone` | `string` | Sí | Teléfono válido según las reglas de dominio del backend. |
| `email` | `string` | Sí | Correo válido y no registrado previamente. |
| `password` | `string` | Sí | Entre 8 y 128 caracteres. Nunca se envía ni se devuelve el hash. |
| `android_id` | `string` | Sí | Identificador no vacío y no vinculado previamente a otra cuenta. |

### Response `201 Created`

```json
{
  "id": "<user-uuid>",
  "email": "laura.perez@example.com",
  "role": "patient"
}
```

La respuesta no incluye la contraseña ni el hash. El endpoint de registro no devuelve JWT; después de recibir `201`, el frontend debe usar `/auth/login` con el correo y la contraseña recién registrados.

### Errors

#### `409 Conflict`

Se devuelve cuando ya existe una cuenta con el correo, la cédula o el `android_id` enviado:

```json
{
  "detail": "email is already registered"
}
```

El mensaje exacto puede identificar el campo en conflicto, pero nunca debe incluir SQL, stack traces, contraseñas ni información sensible.

#### `422 Unprocessable Content`

Se devuelve cuando faltan campos o no cumplen las reglas de formato, por ejemplo, email inválido, contraseña corta, teléfono inválido, fecha ausente o `android_id` vacío.

## 4. Actualizar Perfil - A-006

> **Estado:** Implementado y disponible. Requiere token Bearer de autenticación.

Permite a un paciente modificar su correo electrónico y/o su número de teléfono. El sistema exige que hayan transcurrido al menos 24 horas desde la última modificación del perfil.

### Request

```http
PUT /api/v1/usuarios/perfil
Authorization: Bearer <jwt>
Content-Type: application/json
```

```json
{
  "email": "nuevo.correo@example.com",
  "phone": "79876543"
}
```

Todos los campos son opcionales en el body; se puede enviar solo `email`, solo `phone` o ambos.

### Response `200 OK`

```json
{
  "message": "Perfil actualizado exitosamente",
  "id": "<user-uuid>",
  "email": "nuevo.correo@example.com",
  "phone": "79876543",
  "last_profile_update": "2026-11-13T17:30:00+00:00"
}
```

### Errors

#### `401 Unauthorized`

Token inválido, expirado o faltante.

#### `403 Forbidden`

Se deniega la modificación si no han transcurrido 24 horas desde la última actualización de perfil. Se informa el tiempo restante:

```json
{
  "detail": "Profile modification is locked. Please wait 14h 23m remaining."
}
```

#### `409 Conflict`

El nuevo correo electrónico ya está registrado por otro usuario:

```json
{
  "detail": "email is already registered"
}
```

#### `422 Unprocessable Content`

Formato de correo inválido o número de teléfono no cumple el formato boliviano (debe iniciar con 6 o 7 y tener 8 dígitos numéricos).

---

## 5. Eliminar Cuenta - A-007

> **Estado:** Implementado y disponible. Requiere token Bearer de autenticación y contraseña actual como challenge.

Permite al paciente dar de baja definitiva a su cuenta. Al confirmarse la contraseña, el sistema elimina la cuenta, desvincula el hardware (`android_id`) y libera el número de carnet (`identity_card`) de la base de datos para que puedan ser reutilizados en el futuro.

### Request

```http
DELETE /api/v1/usuarios/cuenta
Authorization: Bearer <jwt>
Content-Type: application/json
```

```json
{
  "password": "CurrentPassword123"
}
```

### Response `200 OK`

```json
{
  "message": "Cuenta eliminada exitosamente. Se ha desvinculado el dispositivo y liberado la identidad."
}
```

### Errors

#### `401 Unauthorized`

Token inválido o contraseña incorrecta:

```json
{
  "detail": "Incorrect password"
}
```

#### `422 Unprocessable Content`

Body malformado o campo `password` vacío.

## Flujo recomendado para registro y login

1. El frontend valida campos básicos localmente.
2. Envía `POST /api/v1/usuarios`.
3. Si recibe `201`, redirige al login o inicia la pantalla de autenticación.
4. Envía `POST /api/v1/auth/login`.
5. Guarda el `access_token` y lo envía como Bearer token en futuras rutas protegidas.
6. Si recibe `409`, marca el campo indicado como ya registrado.
7. Si recibe `422`, muestra los errores asociados a cada campo.

## Documentación automática de FastAPI

Cuando el backend esté levantado, FastAPI publicará automáticamente:

```text
Swagger UI: http://localhost:8000/docs
OpenAPI JSON: http://localhost:8000/openapi.json
ReDoc: http://localhost:8000/redoc
```

Estas URLs requieren ejecutar la aplicación. Este archivo permite implementar el frontend sin iniciar Docker; los ejemplos y contratos anteriores son la referencia mientras A-005 sigue pendiente.
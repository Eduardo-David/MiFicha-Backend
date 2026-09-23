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
| `POST` | `/usuarios` | Pendiente: A-005 | Crear una cuenta, su identidad y su dispositivo. |

Los endpoints para editar perfil y eliminar cuenta no forman parte de esta rama ni de este contrato.

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

> **Estado:** Pendiente de implementación en el backend. Este contrato es el objetivo que debe cumplir la implementación de A-005.

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
  "detail": "The email is already registered"
}
```

El mensaje exacto puede identificar el campo en conflicto, pero nunca debe incluir SQL, stack traces, contraseñas ni información sensible.

#### `422 Unprocessable Entity`

Se devuelve cuando faltan campos o no cumplen las reglas de formato, por ejemplo, email inválido, contraseña corta, teléfono inválido, fecha ausente o `android_id` vacío.

#### `500 Internal Server Error`

Representa un fallo inesperado del servidor. El frontend debe mostrar un mensaje genérico y no intentar interpretar detalles internos.

### Garantías de A-005

Cuando A-005 esté implementado:

- Se crearán `Persona`, `User` y `Device` asociados al mismo registro.
- El usuario se creará con rol `patient`.
- La contraseña se almacenará únicamente como hash Bcrypt.
- El registro será atómico: no quedarán registros parciales si falla uno de los pasos.
- `email`, `identity_card` y `android_id` no podrán reutilizarse.
- La validación OCR se consumirá mediante el puerto `IOCRService`.
- El adaptador usado en pruebas será un mock; no habrá integración con un proveedor OCR real en A-005.

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
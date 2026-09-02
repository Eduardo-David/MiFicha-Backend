# MiFicha Backend API

Sistema de reservas médicas basado en **Arquitectura Hexagonal** con FastAPI y PostgreSQL.

## 📋 Descripción del Proyecto

MiFicha es una API backend para gestionar un sistema de reservas de fichas médicas. Implementa arquitectura hexagonal (puertos y adaptadores) con separación clara entre capas de dominio, aplicación e infraestructura.

### Características Principales
- ✅ Arquitectura Hexagonal (Puertos y Adaptadores)
- ✅ FastAPI como framework web
- ✅ PostgreSQL como base de datos
- ✅ Docker y Docker Compose para containerización
- ✅ Type Hints y validación con Pydantic
- ✅ Inyección de dependencias
- ✅ Casos de uso: Registro de cuentas, autenticación (próximamente)

---

## 🚀 Instalación y Ejecución

### Opción 1: Con Docker (Recomendado)

#### Prerequisitos
- [Docker](https://www.docker.com/products/docker-desktop) v20+
- [Docker Compose](https://docs.docker.com/compose/) v1.29+

#### Pasos:

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd MiFicha-Backend
   ```

2. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Edita .env si es necesario (para desarrollo, los valores por defecto están listos)
   ```

3. **Iniciar los servicios**
   ```bash
   docker-compose up -d
   ```

4. **Verificar los servicios**
   ```bash
   # Verificar que los contenedores están corriendo
   docker-compose ps

   # Ver logs de la API
   docker-compose logs mificha-api

   # Ver logs de la BD
   docker-compose logs mificha-db
   ```

5. **Acceder a la API**
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
   - Health Check: [http://localhost:8000/](http://localhost:8000/)

6. **Acceder a pgAdmin (opcional)**
   - URL: [http://localhost:5050](http://localhost:5050)
   - Email: `admin@mificha.local`
   - Password: `admin123`
   - Conexión a BD: `mificha-db` (host), `mificha_user` (usuario), `mificha_password` (contraseña)

#### Comandos Útiles Docker

```bash
# Detener servicios
docker-compose down

# Detener y limpiar volúmenes (¡CUIDADO! Elimina datos de BD)
docker-compose down -v

# Reconstruir imagen
docker-compose build

# Ver logs en tiempo real
docker-compose logs -f mificha-api

# Ejecutar comando en contenedor
docker-compose exec mificha-api python -m pytest

# Acceder al contenedor
docker-compose exec mificha-api bash
```

---

### Opción 2: Sin Docker (Instalación Local)

#### Prerequisitos
- Python 3.10+
- PostgreSQL 13+
- pip (gestor de paquetes de Python)

#### Pasos:

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd MiFicha-Backend
   ```

2. **Crear ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos**
   - Crear base de datos PostgreSQL llamada `mificha_db`
   - Ejecutar script de inicialización:
     ```bash
     psql -U postgres -d mificha_db -f scripts/init-db.sql
     ```

5. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Edita .env con tus credenciales de BD
   ```

6. **Ejecutar el servidor**
   ```bash
   uvicorn main:app --reload
   ```

7. **Acceder a la API**
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📊 Estructura del Proyecto

```
MiFicha-Backend/
├── domain/                 # Capa de Dominio (lógica de negocio pura)
│   ├── __init__.py
│   └── entities.py        # Entidades: Persona, Solicitante, Cuenta, DispositivoMovil
├── application/            # Capa de Aplicación (casos de uso)
│   ├── __init__.py
│   ├── ports.py           # Puertos (interfaces abstractas)
│   └── services.py        # Servicios (casos de uso)
├── infrastructure/         # Capa de Infraestructura (frameworks, adaptadores)
│   ├── __init__.py
│   ├── controllers.py     # Controladores (endpoints FastAPI)
│   ├── adapters.py        # Adaptadores (repositorios, hashing)
│   └── dtos.py            # DTOs (validación de entrada/salida)
├── scripts/
│   └── init-db.sql        # Script de inicialización de BD
├── main.py                # Punto de entrada de la aplicación
├── requirements.txt       # Dependencias del proyecto
├── Dockerfile             # Configuración de imagen Docker
├── docker-compose.yml     # Orquestación de servicios
├── .env.example           # Variables de entorno (plantilla)
├── .env                   # Variables de entorno (desarrollo local)
├── .gitignore             # Archivos a ignorar en git
└── README.md              # Este archivo
```

---

## 🔄 Flujo de Registro de Cuenta

```
Cliente HTTP
    ↓
POST /cuentas/registro (RegistroCuentaRequest)
    ↓
Controlador (CuentaController)
    ├─ Valida DTO con Pydantic
    ├─ Inyecta AdministrarCuentaService
    └─ Llama al caso de uso
         ↓
    Servicio (AdministrarCuentaService)
         ├─ Verifica regla: 1 dispositivo = 1 cuenta
         ├─ Hashea contraseña
         ├─ Crea entidades del dominio
         ├─ Vincula dispositivo y solicitante
         └─ Persiste mediante repositorio
              ↓
         Adaptador (InMemoryCuentaRepository)
              └─ Almacena en memoria
                   ↓
    Respuesta: RegistroCuentaResponse (201 Created)
         ↓
Cliente HTTP
```

---

## 🧪 Testing

### Probar el Endpoint con cURL

```bash
curl -X POST "http://localhost:8000/cuentas/registro" \
  -H "Content-Type: application/json" \
  -d '{
    "nombres": "Juan",
    "apellidoPaterno": "Pérez",
    "apellidoMaterno": "García",
    "telefono": "555-1234",
    "numeroCarnet": "12345678",
    "fechaNacimiento": "1990-01-15",
    "correo": "juan.perez@email.com",
    "password": "MiPassword123!",
    "androidID": "device_001"
  }'
```

### Respuesta Esperada

```json
{
  "cuenta_id": "550e8400-e29b-41d4-a716-446655440000",
  "mensaje": "Cuenta creada exitosamente"
}
```

### Errores Comunes

**Error 400 - Dispositivo ya registrado:**
```json
{
  "detail": "El dispositivo ya tiene una cuenta vinculada."
}
```

**Error 422 - Validación de entrada:**
```json
{
  "detail": [
    {
      "loc": ["body", "correo"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

---

## 📝 API Endpoints

### Salud del Sistema

- **GET** `/` - Health check
  ```bash
  curl http://localhost:8000/
  ```

### Gestión de Cuentas

- **POST** `/cuentas/registro` - Registrar nueva cuenta
  - Body: `RegistroCuentaRequest`
  - Response: `RegistroCuentaResponse` (201 Created)

### Endpoints Documentados

Todos los endpoints están documentados en Swagger:
- [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
- [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc)

---

## ⚙️ Configuración

### Variables de Entorno

Ver archivo `.env.example` para todas las variables disponibles. Las principales son:

```env
# Aplicación
ENVIRONMENT=development
LOG_LEVEL=INFO

# Base de Datos
DATABASE_URL=postgresql://mificha_user:mificha_password@mificha-db:5432/mificha_db

# JWT (para implementar)
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

---

## 🔐 Seguridad

### Implementado
- ✅ Hashing de contraseñas (SHA256)
- ✅ Type hints y validación de tipos
- ✅ Validación de entrada con Pydantic
- ✅ Usuario no-root en Docker
- ✅ Health checks automáticos

### Pendiente
- ⚠️ JWT Authentication
- ⚠️ HTTPS/TLS
- ⚠️ Rate Limiting
- ⚠️ CORS configurado
- ⚠️ Encriptación de datos sensibles

---

## 🚀 Próximos Pasos

1. **Fase 1 - Autenticación** (Semana 1-2)
   - Implementar JWT
   - Endpoint de Login
   - Endpoint de Logout

2. **Fase 2 - Persistencia** (Semana 3-4)
   - Conectar a PostgreSQL real
   - Crear ORM models (SQLAlchemy)
   - Migrations

3. **Fase 3 - Completitud** (Semana 5+)
   - Otros casos de uso
   - Tests automatizados
   - CI/CD pipeline

---

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 📞 Contacto

- **Email:** support@mificha.com
- **Issues:** [GitHub Issues](https://github.com/username/MiFicha-Backend/issues)

---

## 📚 Recursos Adicionales

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Arquitectura Hexagonal](https://en.wikipedia.org/wiki/Hexagonal_architecture)

---

**Última actualización:** 2026-01-09  
**Versión:** 1.0.0  
**Estado:** MVP - En Desarrollo

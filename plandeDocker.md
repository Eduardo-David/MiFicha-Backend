# Plan de Implementación de Docker para Backend

## 1. Contenedores y Entorno (Docker)

- **Dockerfile:**
  - Optimizado para FastAPI con Python 3.10+.
  - Usa buenas prácticas: expone puerto 8000, ejecuta con uvicorn, evita ejecutar como root.

- **docker-compose.yml:**
  - Define dos servicios interconectados: la aplicación FastAPI y una base de datos PostgreSQL 15+.

- **.env.example:**
  - Especifica las variables de entorno necesarias (ej. `DATABASE_URL`, `POSTGRES_USER`).

## 2. Implementación de Adaptadores (PostgreSQL)

- **Configuración de Conexión:**
  - Configura la conexión PostgreSQL usando `SQLAlchemy` o `asyncpg` en la capa de Infraestructura.

- **PostgresCuentaRepository:**
  - Implementa la interfaz `ICuentaRepository` de la capa de Aplicación.

- **PostgresDispositivoRepository:**
  - Implementa la interfaz `IDispositivoRepository`.
  
- **Mapeo de Entidades:**
  - Mapea las entidades del Dominio a las tablas de base de datos sin usar decoradores ORM en la capa de Dominio.

## 3. Testing Automatizado (Pytest)

- **Estructura de Pruebas:**
  - Organiza pruebas en un directorio `tests/`, separando unitarias y de integración.

- **Pruebas Unitarias:**
  - Crea pruebas para `AdministrarCuentaService` usando `unittest.mock` para repositorios falsos.

- **Pruebas de Integración:**
  - Configura el `TestClient` de FastAPI y una base de datos de prueba para probar endpoints de creación de cuenta.

- **Configuración de pytest:**
  - Incluye `pytest.ini` o instrucciones necesarias para ejecutar la suite de pruebas.
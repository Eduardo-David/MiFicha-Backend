# 🐳 Guía de Dockerización - MiFicha Backend

Esta guía explica cómo usar Docker y Docker Compose para ejecutar el proyecto MiFicha Backend.

## 📋 Índice

1. [Prerequisitos](#prerequisitos)
2. [Estructura Docker](#estructura-docker)
3. [Inicio Rápido](#inicio-rápido)
4. [Servicios Disponibles](#servicios-disponibles)
5. [Comandos Útiles](#comandos-útiles)
6. [Troubleshooting](#troubleshooting)
7. [Desarrollo con Docker](#desarrollo-con-docker)
8. [Deployment](#deployment)

---

## 📦 Prerequisitos

- **Docker** v20.0+
- **Docker Compose** v1.29+ (incluido en Docker Desktop)
- **Git** para clonar el repositorio

### Verificar Instalación

```bash
docker --version
docker-compose --version
```

### Instalación

- **Windows/Mac:** [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux:** [Instalación oficial](https://docs.docker.com/engine/install/)

---

## 🏗️ Estructura Docker

### Dockerfile - Multi-stage Build

```dockerfile
Stage 1: Builder
├── Python 3.10-slim
├── Instala gcc (solo para compilar)
└── Instala dependencias en venv

Stage 2: Runtime (Final)
├── Python 3.10-slim (imagen más pequeña)
├── Copia venv del Builder
├── Copia código fuente
├── Usuario no-root (mificha)
├── Health check configurado
└── Exposición del puerto 8000
```

**Ventajas:**
- ✅ Imagen más pequeña (~300MB vs ~800MB)
- ✅ Seguridad mejorada (usuario no-root)
- ✅ Sin herramientas de compilación en producción
- ✅ Health checks automáticos

### docker-compose.yml - Orquestación

Tres servicios principales:

1. **mificha-api** - FastAPI backend
2. **mificha-db** - PostgreSQL 15
3. **pgadmin** (opcional) - Gestor de BD

---

## 🚀 Inicio Rápido

### Opción 1: PowerShell (Windows)

```powershell
# Dar permisos de ejecución al script
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Iniciar servicios
.\docker-dev.ps1 -Action up

# Ver logs
.\docker-dev.ps1 -Action logs

# Acceder al contenedor
.\docker-dev.ps1 -Action shell

# Detener servicios
.\docker-dev.ps1 -Action down
```

### Opción 2: Make (Linux/Mac)

```bash
# Iniciar servicios
make up

# Ver logs
make logs

# Acceder al contenedor
make shell

# Detener servicios
make down
```

### Opción 3: Docker Compose Directo

```bash
# Iniciar en background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

---

## 🔧 Servicios Disponibles

### 1. API FastAPI (mificha-api)

```
Puerto: 8000
URL: http://localhost:8000
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
Health Check: GET http://localhost:8000/
```

**Características:**
- Hot-reload en desarrollo
- Validación automática con Pydantic
- Documentación interactiva
- Health check cada 30 segundos

**Variables de entorno:**
```env
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=True
DATABASE_URL=postgresql://mificha_user:mificha_password@mificha-db:5432/mificha_db
```

### 2. PostgreSQL (mificha-db)

```
Host: localhost (desde host) o mificha-db (desde contenedor)
Puerto: 5432
Usuario: mificha_user
Contraseña: mificha_password
Base de Datos: mificha_db
```

**Características:**
- Imagen Alpine (pequeña y eficiente)
- Inicialización automática con init-db.sql
- Health check integrado
- Persistencia de datos en volumen

**Conectarse desde el host:**
```bash
psql -h localhost -p 5432 -U mificha_user -d mificha_db
```

### 3. pgAdmin (mificha-pgadmin)

```
URL: http://localhost:5050
Email: admin@mificha.local
Contraseña: admin123
Perfil: dev (ejecutar con: docker-compose --profile dev up)
```

**Características:**
- Gestor web para PostgreSQL
- Visualización de datos y tablas
- Ejecución de queries
- Uso opcional (perfil dev)

---

## 📝 Comandos Útiles

### Gestión de Servicios

```bash
# Iniciar en background
docker-compose up -d

# Iniciar en foreground (ver logs)
docker-compose up

# Detener sin eliminar volúmenes
docker-compose down

# Detener y eliminar volúmenes (¡CUIDADO! Pierde datos de BD)
docker-compose down -v

# Reconstruir imágenes sin cache
docker-compose build --no-cache

# Reiniciar servicios
docker-compose restart

# Reiniciar un servicio específico
docker-compose restart mificha-api
```

### Logs y Debugging

```bash
# Ver logs de todos los servicios
docker-compose logs

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs mificha-api

# Ver últimas 100 líneas
docker-compose logs --tail=100

# Ver logs de múltiples servicios
docker-compose logs mificha-api mificha-db
```

### Ejecución de Comandos

```bash
# Ejecutar comando en contenedor
docker-compose exec mificha-api python -c "import sys; print(sys.version)"

# Abrir shell bash
docker-compose exec mificha-api bash

# Ejecutar pytest
docker-compose exec mificha-api python -m pytest

# Acceder a la BD
docker-compose exec mificha-db psql -U mificha_user -d mificha_db

# Ejecutar migraciones (cuando se implemente)
docker-compose exec mificha-api alembic upgrade head
```

### Inspección

```bash
# Ver estado de los servicios
docker-compose ps

# Ver estado detallado
docker-compose ps --all

# Ver configuración
docker-compose config

# Ver uso de recursos
docker stats

# Inspeccionar un contenedor
docker inspect mificha-api
```

### Mantenimiento

```bash
# Eliminar contenedores no usados
docker container prune

# Eliminar imágenes no usadas
docker image prune

# Eliminar volúmenes no usados
docker volume prune

# Limpieza completa
docker system prune -a

# Ver información del sistema
docker system df
```

---

## 🔍 Troubleshooting

### Puerto 8000 o 5432 ya está en uso

```bash
# Opción 1: Cambiar puerto en docker-compose.yml
# Cambiar "8000:8000" a "8001:8000"

# Opción 2: Liberar puerto
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Error: "Cannot connect to Docker daemon"

```bash
# Windows/Mac
# - Asegurate de que Docker Desktop está ejecutándose
# - En WSL2, reinicia el servicio: wsl --shutdown

# Linux
# - Inicia el servicio de Docker
sudo systemctl start docker

# - Agrega tu usuario al grupo docker
sudo usermod -aG docker $USER
```

### Contenedor se reinicia constantemente

```bash
# Ver logs detallados
docker-compose logs mificha-api

# Verificar health check
docker inspect mificha-api | grep -A 10 HealthCheck

# Aumentar start_period en docker-compose.yml
# de start_period=40s a start_period=60s
```

### BD no inicializa correctamente

```bash
# 1. Eliminar volumen de BD
docker-compose down -v

# 2. Reconstruir imagen
docker-compose build --no-cache

# 3. Iniciar nuevamente
docker-compose up -d

# 4. Ver logs
docker-compose logs mificha-db
```

### Cambios en el código no se reflejan

```bash
# En desarrollo, con hot-reload debe ser automático
# Si no funciona:

# 1. Reconstruir imagen
docker-compose build

# 2. Reiniciar servicio
docker-compose restart mificha-api

# Nota: Los cambios en requirements.txt requieren rebuild
```

---

## 🏗️ Desarrollo con Docker

### Flujo de Desarrollo

```
1. Editar archivos locales
   ↓
2. Docker monta el volumen ./:/app
   ↓
3. Uvicorn detecta cambios (hot-reload)
   ↓
4. Servidor se recarga automáticamente
   ↓
5. Probar en navegador sin restart manual
```

### Agregar Nuevas Dependencias

```bash
# 1. Agregar a requirements.txt
echo "nueva-libreria==1.0.0" >> requirements.txt

# 2. Opción A: Rebuild automático (si el contenedor está corriendo)
# Los cambios se aplicarán en el próximo comando

# 2. Opción B: Reconstruir explícitamente
docker-compose build --no-cache

# 3. Reiniciar
docker-compose restart mificha-api
```

### Debugging

```bash
# Agregar puntos de parada en el código
# Ej: import pdb; pdb.set_trace()

# Ejecutar en modo debugging
docker-compose exec mificha-api python -m pdb main.py

# O usar debugger de VS Code
# Ver .vscode/launch.json para configuración
```

### Testing

```bash
# Ejecutar todos los tests
docker-compose exec mificha-api python -m pytest

# Ejecutar tests con cobertura
docker-compose exec mificha-api python -m pytest --cov=. --cov-report=html

# Ejecutar test específico
docker-compose exec mificha-api python -m pytest tests/test_services.py

# Ver reporte
open htmlcov/index.html
```

---

## 🚀 Deployment

### Desarrollo → Producción

#### 1. Variables de Entorno

```bash
# Crear .env.production
cp .env.example .env.production

# Cambiar valores sensibles
# DATABASE_URL=postgresql://prod_user:strong_password@prod-db.aws.com:5432/prod_db
# SECRET_KEY=super-secret-production-key
# ENVIRONMENT=production
# DEBUG=False
```

#### 2. Archivo Compose para Producción

```bash
# Usar solo docker-compose.yml (no override)
docker-compose -f docker-compose.yml up -d --env-file .env.production
```

#### 3. Optimizar Dockerfile

```dockerfile
# Agregar argumentos de build
ARG ENVIRONMENT=production

# Usar argumentos en RUN
RUN if [ "$ENVIRONMENT" = "production" ]; then \
    pip install --no-dev -r requirements.txt; \
    else pip install -r requirements.txt; fi
```

#### 4. Ejecutar con Docker Swarm o Kubernetes

```bash
# Docker Swarm
docker stack deploy -c docker-compose.yml mificha

# Kubernetes (usando docker-compose)
kompose convert -f docker-compose.yml -o k8s/
```

### Monitoreo en Producción

```bash
# Health check automático
curl https://api.mificha.com/

# Logs persistentes
# Usar logging driver: json-file con size-limit
# Ver docker-compose-prod.yml para configuración

# Alertas
# Configurar con Sentry, DataDog, New Relic, etc.
```

---

## 🔐 Seguridad en Docker

### Best Practices Implementadas

✅ **Usuario no-root:** Imagen ejecuta como usuario `mificha`
✅ **Multi-stage build:** Sin herramientas de compilación en runtime
✅ **Health checks:** Validación continua de salud del contenedor
✅ **Volúmenes específicos:** No monta más de lo necesario

### Mejoras Futuras

⚠️ **Secrets de BD:** Usar Docker Secrets en Swarm
⚠️ **Network segura:** Usar networks específicas
⚠️ **Imagen scaneo:** Escanear con Trivy o Snyk
⚠️ **Registries privados:** Usar registries privados para imágenes
⚠️ **HTTPS/TLS:** Configurar SSL certificates

---

## 📊 Performance

### Tamaño de Imagen

```
Base Python 3.10-slim: ~150MB
+ Dependencias:        ~150MB
Total:                 ~300MB

vs. Python 3.10 full:  ~900MB
Ahorro:                ~66%
```

### Optimizaciones

1. **Multi-stage build** - Reduce tamaño final
2. **Alpine Linux** - BD usa alpine (35MB vs 170MB)
3. **Layer caching** - Reutiliza capas no modificadas
4. **Health checks** - Evita contenedores muertos

---

## 📚 Recursos Adicionales

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Compose Specification](https://github.com/compose-spec/compose-spec)
- [PostgreSQL Docker Official Image](https://hub.docker.com/_/postgres)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/docker/)

---

**Última actualización:** 2026-01-09  
**Versión Docker:** 3.9  
**Estado:** Listo para Desarrollo y Deployment

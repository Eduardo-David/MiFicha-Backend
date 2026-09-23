# Propuesta de Optimización de Alcance y Flujo de Trabajo

- **Destinatario:** Lucas / Equipo de Desarrollo
- **Rama Actual:** `feature/UC0-crear-cuenta-api`
- **Módulo:** UC0 – Administrar Usuario (Autenticación & Perfil)
- **Fecha:** 23 de Septiembre de 2026
- **Estado:** Propuesta para Discusión y Aprobación

---

## 1. Contexto y Diagnóstico

Actualmente, el archivo de seguimiento de tareas (`.agent/tasks/task-index.md`) contempla **8 tareas secuenciales (A-001 a A-008)** asignadas a la rama activa `feature/UC0-crear-cuenta-api`.

A la fecha, se han completado con éxito los cimientos críticos del sistema:
- ✅ **A-001:** Setup base del proyecto y PostgreSQL con Docker Compose.
- ✅ **A-002:** Modelado relacional en base de datos (`persona`, `user`, `device`) y migraciones Alembic.
- ✅ **A-003:** Entidades puras y validaciones de negocio boliviano (CI, teléfono, 24h lock).
- ✅ **A-004:** Infraestructura criptográfica (hashing Bcrypt, emisión de tokens JWT y login seguro).

### Problemática Identificada

Acumular las tareas restantes (A-005 a A-008) dentro de esta **misma rama** presenta riesgos significativos:

1. **Riesgo de "Mega-Rama" (*Long-Lived Branch*):** 
   Tener una rama que acumule semanas de trabajo sin mergearse a `develop` genera divergencias profundas con el repositorio base y un alto riesgo de conflictos complejos (*merge conflicts*).
2. **Pull Requests inmanejables:** 
   Un PR que contenga el setup, base de datos, login, registro, edición de perfil y baja de cuenta supera con creces las buenas prácticas de la industria (PRs pequeños y revisables de 200–400 líneas).
3. **Bloqueo para el equipo Frontend (Cosmol App en Flutter):** 
   La aplicación móvil no necesita esperar a que existan los endpoints de "editar perfil" o "eliminar cuenta" para empezar a probar. El bloqueo real para Cosmol App se destraba teniendo **Registro y Login**.
4. **Tareas burocráticas redundantes:** 
   La tarea **A-008** (*Stage-Gate Quality Check*) no aporta funcionalidad; la ejecución de tests unitarios y de integración (`pytest`) es una política obligatoria que debe cumplirse en cada PR, no una tarea formal del backlog.

---

## 2. Propuesta Concreta: Desacoplamiento en Ramas Atómicas

Proponemos ajustar el alcance de la rama actual para cerrarla rápidamente y distribuir el trabajo restante en micro-ramas independientes bajo Git Flow:

```mermaid
gitGraph
   commit id: "develop"
   branch feature/UC0-crear-cuenta-api
   checkout feature/UC0-crear-cuenta-api
   commit id: "A-001 a A-004 (Completadas)"
   commit id: "A-005 (POST /usuarios)"
   checkout develop
   merge feature/UC0-crear-cuenta-api id: "PR Merged a develop"
   
   branch feature/UC0-editar-perfil
   checkout feature/UC0-editar-perfil
   commit id: "PUT /usuarios/perfil"
   
   checkout develop
   branch feature/UC0-eliminar-cuenta
   checkout feature/UC0-eliminar-cuenta
   commit id: "DELETE /usuarios/cuenta"
```

### Plan de Acción en 2 Fases:

#### Fase 1: Cierre Inmediato de la Rama Actual (`feature/UC0-crear-cuenta-api`)
* **Objetivo Único:** Implementar la **Task A-005** (`POST /api/v1/usuarios`), conectando la creación de la persona, usuario y vinculación estricta de hardware (`android_id`).
* **Validación:** Pruebas de integración del flujo de registro.
* **Acción:** Abrir Pull Request y **mergear a `develop`**.
* **Impacto:** Cosmol App queda 100% habilitada para registrar pacientes e iniciar sesión.

#### Fase 2: Ramas Dedicadas para Flujos Secundarios
Una vez que el registro esté en `develop`, los flujos alternativos se trabajarán de forma ágil y paralela si se requiere:
1. **Rama `feature/UC0-editar-perfil`:** 
   * Implementa `PUT /api/v1/usuarios/perfil` con la validación de 24 horas entre modificaciones.
2. **Rama `feature/UC0-eliminar-cuenta`:** 
   * Implementa `DELETE /api/v1/usuarios/cuenta` con desafío de contraseña y liberación del `android_id` y carnet.

---

## 3. Matriz Comparativa: Antes vs. Después

| Criterio | Esquema Anterior (Monolítico) | Propuesta Optimizada (Atómica) |
| :--- | :--- | :--- |
| **Alcance en esta rama** | 8 tareas (A-001 a A-008) | **Solo hasta A-005 (Crear Cuenta)** |
| **Tiempo de vida de la rama** | Semanas / Bloqueada hasta fin de UC0 | **Cierre inmediato tras A-005** |
| **Tamaño del Pull Request** | +2,500 líneas (difícil de auditar) | ~300 líneas (fácil y rápido de revisar) |
| **Riesgo de Merge Conflicts** | Muy Alto | Mínimo |
| **Integración con Cosmol App** | Bloqueada hasta el final | **Inmediata (Registro + Login listos)** |
| **Verificación de Calidad** | Retrasada hasta A-008 | Continua en cada PR |

---

## 4. Próximo Paso Sugerido

Si el equipo da el visto bueno a esta propuesta:
1. Procedemos de inmediato con la implementación de **Task A-005** (Endpoint de creación de cuenta).
2. Verificamos que la suite completa de Pytest pase al 100%.
3. Preparamos el Pull Request para integrar `feature/UC0-crear-cuenta-api` en `develop`.

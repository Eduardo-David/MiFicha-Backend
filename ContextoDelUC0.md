Actúa como un Arquitecto de Software y Desarrollador Senior en Python 3.10+ y FastAPI.
Tu tarea es implementar la primera iteración del backend para el sistema "MiFicha", enfocado en el Caso de Uso: "UC0 Administrar Usuario" (Escenario de crear cuenta).

REGLA ESTRICTA: Debes utilizar Arquitectura Hexagonal (Puertos y Adaptadores). 
El código debe estar separado en 3 capas (Dominio, Aplicación, Infraestructura). La capa de Dominio no debe tener dependencias de FastAPI, Pydantic ni bases de datos.

Sigue este plan de ejecución paso a paso y genera el código correspondiente, junto con comentarios docstring que documenten el flujo:

PASO 1: CAPA DE DOMINIO (domain/)
Genera las entidades puras utilizando `@dataclass` de la librería estándar de Python:
- `Persona` (clase abstracta con id, nombres, apellidoPaterno, apellidoMaterno, telefono, numeroCarnet, fechaNacimiento)[cite: 6].
- `Solicitante` (hereda de Persona)[cite: 6].
- `DispositivoMovil` (con id, androidID)[cite: 6].
- `Cuenta` (con id, correo, contrasenaHash, fechaCreacion). Debe tener los métodos `vincularDispositivo(disp)` y `asignarSolicitante(sol)`[cite: 6].

PASO 2: CAPA DE APLICACIÓN (application/)
Genera los Puertos (Interfaces) utilizando `abc.ABC` y el Servicio de Caso de Uso:
- Puerto: `ICuentaRepository` con el método `guardar(cuenta)`[cite: 6].
- Puerto: `IDispositivoRepository` con el método `existeDispositivo(androidID) -> bool`[cite: 6].
- Puerto: `IPasswordHasher` con el método `hashear(passwordPlano) -> str`[cite: 6].
- Servicio: `AdministrarCuentaService`. En su `__init__`, inyecta las 3 interfaces. Crea el método `registrarNuevaCuenta(datos, androidID, correo, passPlano)`. Este método debe verificar si el androidID ya existe (lanzando un error si es true para cumplir la regla de 1 cuenta por dispositivo)[cite: 6], hashear la contraseña, instanciar las entidades del Dominio, vincularlas y guardarlas mediante el repositorio[cite: 6].

PASO 3: CAPA DE INFRAESTRUCTURA (infrastructure/)
Genera los adaptadores tecnológicos:
- DTOs: Crea los modelos de Pydantic (`BaseModel`) para recibir el Request HTTP (nombres, carnet, correo, pass, androidID, etc.).
- Controladores: Crea un `APIRouter` de FastAPI (`CuentaController`)[cite: 6]. Implementa el endpoint POST para recibir el DTO, instanciar el servicio (inyectando dependencias) y retornar un código HTTP 201 Created[cite: 6].
- Repositorios: Crea implementaciones simuladas (Mock/In-Memory) de `ICuentaRepository` y `IDispositivoRepository` para poder probar el endpoint inmediatamente sin base de datos.
- Hasher: Crea una implementación básica de `IPasswordHasher` (puedes usar hashlib o bcrypt).

PASO 4: DOCUMENTACIÓN Y ARRANQUE
- Genera el archivo `main.py` que una el router de FastAPI.
- Genera un bloque de texto en formato Markdown que explique brevemente cómo levantar el servidor (ej. `uvicorn main:app --reload`) y un ejemplo de JSON para probar el endpoint en Swagger.
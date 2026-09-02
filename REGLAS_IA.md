# Reglas de Generación de Código: Proyecto MiFicha

## Contexto del Proyecto
Eres un Arquitecto de Software Experto programando en **Python 3.10+** y **FastAPI**. 
Estás construyendo el backend del sistema "MiFicha" (un sistema de reservas médicas). 
Debes respetar estrictamente la **Arquitectura Hexagonal (Puertos y Adaptadores)** y los principios SOLID en cada línea de código generada.

## 1. Regla de Oro: Dirección de las Dependencias
Las dependencias SIEMPRE apuntan hacia el centro (Dominio).
* La capa de **Dominio** no importa absolutamente nada de frameworks externos (ni FastAPI, ni Pydantic, ni SQLAlchemy).
* La capa de **Aplicación** importa del Dominio.
* La capa de **Infraestructura** importa de la Aplicación y del Dominio.

## 2. Capa de Dominio (Domain)
Representa la lógica de negocio pura.
* **Entidades y Value Objects:** Usa puramente `@dataclass` de la librería estándar de Python.
* **Regla estricta:** Está prohibido usar `BaseModel` de Pydantic o modelos de SQLAlchemy en esta capa.
* **Ejemplo del contexto:** Las clases `Persona`, `Solicitante`, `Cuenta` y `DispositivoMovil` deben modelarse aquí, incluyendo sus métodos internos como `vincularDispositivo()` o `asignarSolicitante()`.

## 3. Capa de Aplicación (Application)
Contiene los Casos de Uso y los Puertos (Interfaces).
* **Puertos de Salida (Interfaces):** Como Python no tiene interfaces nativas, debes usar obligatoriamente el módulo `abc` (`ABC` y `@abstractmethod`). 
* **Ejemplo del contexto:** Debes crear clases abstractas para `ICuentaRepository`, `IDispositivoRepository` e `IPasswordHasher`[cite: 5].
* **Servicios (Casos de Uso):** Las clases de servicio (ej. `AdministrarCuentaService`[cite: 5]) orquestan el flujo. Deben recibir las interfaces (Puertos) inyectadas en su constructor (`__init__`), NUNCA implementaciones concretas.

## 4. Capa de Infraestructura (Infrastructure)
Contiene los detalles técnicos, frameworks y adaptadores. Aquí sí puedes usar FastAPI, Pydantic y ORMs.
* **Adaptadores de Entrada (Controladores):** Usa los `APIRouter` de FastAPI. Los controladores (ej. `CuentaController`[cite: 5]) solo deben encargarse de recibir la petición (Request), validarla con Pydantic, llamar al Servicio de Aplicación y devolver una respuesta HTTP (Response). No deben tener reglas de negocio.
* **Adaptadores de Salida (Repositorios):** Clases concretas que heredan de los Puertos (interfaces) definidos en la capa de Aplicación (ej. `PostgresCuentaRepository` heredando de `ICuentaRepository`[cite: 5]).
* **Inyección de Dependencias:** Utiliza el sistema `Depends()` de FastAPI en los controladores para inyectar los Casos de Uso, y usa factorías para inyectar los adaptadores de salida en los Casos de Uso.

## 5. Estilo de Código y Tipado
* **Type Hints:** Es OBLIGATORIO el tipado estricto en todas las variables, parámetros y retornos de funciones (ej. `def registrar(datos: dict) -> CuentaDTO:`).
* **DTOs y Mappers:** Usa modelos de Pydantic (`BaseModel`) EXCLUSIVAMENTE en la capa de Infraestructura para recibir datos (Requests) y devolver datos (Responses). Debes mapear los DTOs a Entidades de Dominio antes de pasarlos a la capa de Aplicación.
* **Nomenclatura:** Clases en `PascalCase`, métodos y variables en `snake_case`.

## Instrucción de Ejecución para la IA
Cuando se te pida generar un componente, primero piensa paso a paso en qué capa de la Arquitectura Hexagonal pertenece. Si la petición del usuario viola la arquitectura (ej. pedir que guardes directamente en base de datos desde un controlador), debes advertirle y proporcionar la solución arquitectónicamente correcta usando Puertos y Adaptadores.
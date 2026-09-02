from fastapi import FastAPI
from infrastructure.controllers import router as cuenta_router

app = FastAPI(
    title="MiFicha Backend API", 
    description="API para el sistema de reservas médicas basado en Arquitectura Hexagonal.",
    version="1.0.0"
)

# Integración del router del controlador de cuentas
app.include_router(cuenta_router)

@app.get("/", tags=["Health"])
def health_check():
    """Endpoint básico para verificar que la API está viva."""
    return {"status": "ok", "message": "API MiFicha funcionando"}

@app.get("/health", tags=["Health"])
def health_endpoint():
    """Endpoint diseñado para comprobaciones del contenedor y monitoreo."""
    return {"status": "healthy", "service": "MiFicha Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

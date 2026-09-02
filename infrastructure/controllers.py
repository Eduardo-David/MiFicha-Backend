from fastapi import APIRouter, HTTPException, status, Depends
from infrastructure.dtos import RegistroCuentaRequest, RegistroCuentaResponse
from infrastructure.adapters import InMemoryCuentaRepository, InMemoryDispositivoRepository, SHA256PasswordHasher
from application.services import AdministrarCuentaService

router = APIRouter(prefix="/cuentas", tags=["Cuentas"])

# Instancias simuladas globales para mantener el estado en memoria durante la ejecución de pruebas
cuenta_repo_mock = InMemoryCuentaRepository()
dispositivo_repo_mock = InMemoryDispositivoRepository()
hasher_mock = SHA256PasswordHasher()

def get_administrar_cuenta_service() -> AdministrarCuentaService:
    """Factoría para inyectar las dependencias en el Caso de Uso."""
    return AdministrarCuentaService(cuenta_repo_mock, dispositivo_repo_mock, hasher_mock)

@router.post("/registro", response_model=RegistroCuentaResponse, status_code=status.HTTP_201_CREATED)
def registrar_cuenta(
    request: RegistroCuentaRequest,
    service: AdministrarCuentaService = Depends(get_administrar_cuenta_service)
):
    """Endpoint para registrar una nueva cuenta y vincular dispositivo/solicitante."""
    try:
        datos_persona = {
            "nombres": request.nombres,
            "apellidoPaterno": request.apellidoPaterno,
            "apellidoMaterno": request.apellidoMaterno,
            "telefono": request.telefono,
            "numeroCarnet": request.numeroCarnet,
            "fechaNacimiento": request.fechaNacimiento
        }
        
        # Llamada al Caso de Uso
        cuenta = service.registrarNuevaCuenta(
            datos_persona=datos_persona,
            androidID=request.androidID,
            correo=request.correo,
            passPlano=request.password
        )
        
        # Simular que la base de datos guardó el dispositivo para la siguiente validación
        dispositivo_repo_mock.agregar_dispositivo(request.androidID)
        
        return RegistroCuentaResponse(
            cuenta_id=cuenta.id,
            mensaje="Cuenta creada exitosamente"
        )
    except ValueError as e:
        # Manejo de reglas de negocio fallidas (Ej: Dispositivo ya registrado)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

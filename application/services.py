import uuid
from typing import Dict, Any
from application.ports import ICuentaRepository, IDispositivoRepository, IPasswordHasher
from domain.entities import Cuenta, Solicitante, DispositivoMovil

class AdministrarCuentaService:
    """Caso de uso para la administración de cuentas de usuario."""
    
    def __init__(
        self, 
        cuenta_repo: ICuentaRepository, 
        dispositivo_repo: IDispositivoRepository,
        hasher: IPasswordHasher
    ):
        # Inyección de dependencias (Puertos)
        self.cuenta_repo = cuenta_repo
        self.dispositivo_repo = dispositivo_repo
        self.hasher = hasher

    def registrarNuevaCuenta(
        self, 
        datos_persona: Dict[str, Any], 
        androidID: str, 
        correo: str, 
        passPlano: str
    ) -> Cuenta:
        """
        Registra una nueva cuenta vinculada a un dispositivo y un solicitante.
        Lanza ValueError si el dispositivo ya está registrado.
        """
        # Verificar regla de negocio: 1 cuenta por dispositivo
        if self.dispositivo_repo.existeDispositivo(androidID):
            raise ValueError("El dispositivo ya tiene una cuenta vinculada.")
        
        # Hashear contraseña
        contrasena_hash = self.hasher.hashear(passPlano)
        
        # Instanciar Entidades de Dominio
        dispositivo = DispositivoMovil(id=str(uuid.uuid4()), androidID=androidID)
        solicitante = Solicitante(
            id=str(uuid.uuid4()),
            nombres=datos_persona['nombres'],
            apellidoPaterno=datos_persona['apellidoPaterno'],
            apellidoMaterno=datos_persona['apellidoMaterno'],
            telefono=datos_persona['telefono'],
            numeroCarnet=datos_persona['numeroCarnet'],
            fechaNacimiento=datos_persona['fechaNacimiento']
        )
        cuenta = Cuenta(
            id=str(uuid.uuid4()),
            correo=correo,
            contrasenaHash=contrasena_hash
        )
        
        # Vincular agregados
        cuenta.vincularDispositivo(dispositivo)
        cuenta.asignarSolicitante(solicitante)
        
        # Persistir a través del puerto
        self.cuenta_repo.guardar(cuenta)
        
        return cuenta

    # Nota: Los métodos modificar() y eliminar() han sido omitidos temporalmente 
    # según las reglas de generación del proyecto para esta fase.

import pytest
from unittest.mock import Mock
from application.services import AdministrarCuentaService
from application.ports import ICuentaRepository, IDispositivoRepository, IPasswordHasher

def test_administrar_cuenta_service_guardar():
    cuenta_repo = Mock(ICuentaRepository)
    dispositivo_repo = Mock(IDispositivoRepository)
    password_hasher = Mock(IPasswordHasher)
    service = AdministrarCuentaService(cuenta_repo, dispositivo_repo, password_hasher)
    
    # Simulate successful save
    cuenta_repo.guardar.return_value = None
    dispositivo_repo.existeDispositivo.return_value = False
    
    service.guardar_cuenta(Mock())
    cuenta_repo.guardar.assert_called_once()

    # Simulate error if device already exists
    dispositivo_repo.existeDispositivo.return_value = True
    with pytest.raises(Exception):
service.registrarNuevaCuenta({}, '', '', '')

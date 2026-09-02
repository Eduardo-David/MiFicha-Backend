from pydantic import BaseModel, EmailStr
from datetime import date

class RegistroCuentaRequest(BaseModel):
    """Data Transfer Object para la petición HTTP de registro."""
    nombres: str
    apellidoPaterno: str
    apellidoMaterno: str
    telefono: str
    numeroCarnet: str
    fechaNacimiento: date
    correo: EmailStr
    password: str
    androidID: str

class RegistroCuentaResponse(BaseModel):
    """Data Transfer Object para la respuesta HTTP de registro."""
    cuenta_id: str
    mensaje: str





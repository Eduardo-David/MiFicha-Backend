import urllib.request
import json

data = {
    "nombres": "Juan",
    "apellidoPaterno": "Perez",
    "apellidoMaterno": "Gomez",
    "telefono": "123456",
    "numeroCarnet": "123456",
    "fechaNacimiento": "1990-01-01",
    "correo": "juan@test.com",
    "password": "123",
    "androidID": "dev1"
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/cuentas/registro", 
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as f:
        print(f.status)
        print(f.read().decode('utf-8'))
except Exception as e:
    print(e)
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8'))

# Script para gestionar Docker Compose - MiFicha Backend
# Uso: .\docker-dev.ps1 -Action up|down|logs|build|restart|shell

param(
    [ValidateSet('up', 'down', 'logs', 'build', 'restart', 'shell', 'clean')]
    [string]$Action = 'up',
    
    [string]$Service = 'mificha-api'
)

function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Test-Docker {
    try {
        docker --version | Out-Null
        return $true
    }
    catch {
        Write-Host "Error: Docker no está instalado o no está en el PATH" -ForegroundColor Red
        exit 1
    }
}

# Verificar que Docker está instalado
if (-not (Test-Docker)) {
    exit 1
}

Write-Header "MiFicha Backend - Docker Management"

switch ($Action) {
    'up' {
        Write-Host "Iniciando servicios..." -ForegroundColor Green
        docker-compose up -d
        
        Write-Host "`nEsperando que los servicios estén listos..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        Write-Host "`n✅ Servicios iniciados correctamente" -ForegroundColor Green
        Write-Host "`nAcceso a los servicios:" -ForegroundColor Cyan
        Write-Host "  - API Swagger: http://localhost:8000/docs" -ForegroundColor White
        Write-Host "  - API ReDoc:   http://localhost:8000/redoc" -ForegroundColor White
        Write-Host "  - pgAdmin:     http://localhost:5050" -ForegroundColor White
        Write-Host "  - BD:          localhost:5432" -ForegroundColor White
        
        docker-compose ps
    }
    
    'down' {
        Write-Host "Deteniendo servicios..." -ForegroundColor Yellow
        docker-compose down
        Write-Host "✅ Servicios detenidos" -ForegroundColor Green
    }
    
    'logs' {
        Write-Header "Logs del servicio: $Service"
        docker-compose logs -f $Service
    }
    
    'build' {
        Write-Host "Reconstruyendo imagen..." -ForegroundColor Yellow
        docker-compose build --no-cache
        Write-Host "✅ Imagen reconstruida" -ForegroundColor Green
    }
    
    'restart' {
        Write-Host "Reiniciando servicios..." -ForegroundColor Yellow
        docker-compose restart
        Start-Sleep -Seconds 3
        Write-Host "✅ Servicios reiniciados" -ForegroundColor Green
        docker-compose ps
    }
    
    'shell' {
        Write-Host "Abriendo shell en $Service..." -ForegroundColor Yellow
        docker-compose exec $Service bash
    }
    
    'clean' {
        Write-Host "⚠️  Limpiando todo (incluyendo datos de BD)..." -ForegroundColor Red
        $confirm = Read-Host "¿Estás seguro? (s/n)"
        if ($confirm -eq 's') {
            docker-compose down -v
            Write-Host "✅ Limpieza completada" -ForegroundColor Green
        }
        else {
            Write-Host "Operación cancelada" -ForegroundColor Yellow
        }
    }
}

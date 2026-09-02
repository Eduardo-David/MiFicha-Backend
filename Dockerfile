# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /build

# Instalar dependencias de construcción
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias en un directorio virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

# Metadatos de imagen
LABEL maintainer="MiFicha Development Team"
LABEL description="Backend API para el sistema de reservas médicas MiFicha"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

# Crear usuario no-root por seguridad
RUN useradd -m -u 1000 mificha

WORKDIR /app

# Copiar el ambiente virtual desde builder
COPY --from=builder --chown=mificha:mificha /opt/venv /opt/venv

# Copiar código fuente
COPY --chown=mificha:mificha . .

# Cambiar a usuario no-root
USER mificha

# Exponer puerto
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/', timeout=5)"

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
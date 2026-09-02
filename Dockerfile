# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim as runtime

# Image metadata
LABEL maintainer="MiFicha Development Team" \
      description="Backend API para el sistema de reservas médicas MiFicha" \
      version="1.0.0"

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

# Create non-root user for security
RUN useradd -m -u 1000 mificha && \
    mkdir -p /app && \
    chown -R mificha:mificha /app

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=mificha:mificha /opt/venv /opt/venv

# Copy application source code
COPY --chown=mificha:mificha . .

# Switch to non-root user
USER mificha

# Expose port
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

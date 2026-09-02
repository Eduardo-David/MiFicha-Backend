.PHONY: help up down logs build restart clean shell test install

# Variables
DOCKER_COMPOSE = docker-compose
PYTHON = python
PYTHON_VERSION = 3.10

# Colores para output
BLUE = \033[0;34m
GREEN = \033[0;32m
RED = \033[0;31m
YELLOW = \033[0;33m
NC = \033[0m # No Color

help: ## Mostrar esta ayuda
	@echo "${BLUE}MiFicha Backend - Ayuda de Comandos${NC}"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${GREEN}%-20s${NC} %s\n", $$1, $$2}'
	@echo ""

# Comandos Docker
up: ## Iniciar servicios con Docker
	@echo "${BLUE}Iniciando servicios...${NC}"
	@$(DOCKER_COMPOSE) up -d
	@echo "${GREEN}✅ Servicios iniciados${NC}"
	@echo ""
	@echo "Acceso:"
	@echo "  - API Swagger: http://localhost:8000/docs"
	@echo "  - API ReDoc:   http://localhost:8000/redoc"
	@echo "  - pgAdmin:     http://localhost:5050 (admin/admin123)"
	@echo ""
	@$(DOCKER_COMPOSE) ps

down: ## Detener servicios
	@echo "${YELLOW}Deteniendo servicios...${NC}"
	@$(DOCKER_COMPOSE) down
	@echo "${GREEN}✅ Servicios detenidos${NC}"

logs: ## Ver logs de la API
	@$(DOCKER_COMPOSE) logs -f mificha-api

logs-db: ## Ver logs de la BD
	@$(DOCKER_COMPOSE) logs -f mificha-db

logs-all: ## Ver logs de todos los servicios
	@$(DOCKER_COMPOSE) logs -f

build: ## Reconstruir imagen Docker
	@echo "${YELLOW}Reconstruyendo imagen...${NC}"
	@$(DOCKER_COMPOSE) build --no-cache
	@echo "${GREEN}✅ Imagen reconstruida${NC}"

restart: ## Reiniciar servicios
	@echo "${YELLOW}Reiniciando servicios...${NC}"
	@$(DOCKER_COMPOSE) restart
	@echo "${GREEN}✅ Servicios reiniciados${NC}"
	@$(DOCKER_COMPOSE) ps

shell: ## Abrir shell en el contenedor de la API
	@$(DOCKER_COMPOSE) exec mificha-api bash

shell-db: ## Conectar a la BD PostgreSQL
	@$(DOCKER_COMPOSE) exec mificha-db psql -U mificha_user -d mificha_db

clean: ## Limpiar todo (incluyendo datos de BD)
	@echo "${RED}⚠️  Limpiando todo (incluyendo datos de BD)...${NC}"
	@read -p "¿Estás seguro? (y/n) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_COMPOSE) down -v; \
		echo "${GREEN}✅ Limpieza completada${NC}"; \
	fi

ps: ## Ver estado de los servicios
	@$(DOCKER_COMPOSE) ps

# Comandos de desarrollo local (sin Docker)
install: ## Instalar dependencias locales
	@echo "${BLUE}Instalando dependencias...${NC}"
	@$(PYTHON) -m pip install -r requirements.txt
	@echo "${GREEN}✅ Dependencias instaladas${NC}"

dev: ## Ejecutar servidor en modo desarrollo
	@echo "${BLUE}Iniciando servidor en desarrollo...${NC}"
	@uvicorn main:app --reload

test: ## Ejecutar tests
	@echo "${BLUE}Ejecutando tests...${NC}"
	@$(PYTHON) -m pytest -v

test-cov: ## Ejecutar tests con cobertura
	@echo "${BLUE}Ejecutando tests con cobertura...${NC}"
	@$(PYTHON) -m pytest --cov=. --cov-report=html
	@echo "${GREEN}Reporte en htmlcov/index.html${NC}"

lint: ## Ejecutar linters
	@echo "${BLUE}Ejecutando linters...${NC}"
	@$(PYTHON) -m pylint application domain infrastructure main.py

format: ## Formatear código
	@echo "${BLUE}Formateando código...${NC}"
	@$(PYTHON) -m black .
	@echo "${GREEN}✅ Código formateado${NC}"

# Miscellaneous
version: ## Mostrar versiones
	@echo "Docker version:"
	@docker --version
	@echo ""
	@echo "Docker Compose version:"
	@docker-compose --version
	@echo ""
	@echo "Python version:"
	@$(PYTHON) --version

status: ## Ver estado general del sistema
	@echo "${BLUE}Estado del Sistema${NC}"
	@echo ""
	@echo "Docker:"
	@docker --version && echo "✅ OK" || echo "❌ NO INSTALADO"
	@echo ""
	@echo "Docker Compose:"
	@docker-compose --version && echo "✅ OK" || echo "❌ NO INSTALADO"
	@echo ""
	@echo "Servicios:"
	@$(DOCKER_COMPOSE) ps
	@echo ""

.DEFAULT_GOAL := help

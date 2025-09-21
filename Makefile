# AgentZero Makefile

.PHONY: help build up down restart logs clean test install dev prod

# Variables
DOCKER_COMPOSE = docker-compose
PYTHON = python3
NPM = npm
PROJECT_NAME = agentzero

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)AgentZero - Multi-Agent AI System$(NC)"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Install all dependencies
	@echo "$(GREEN)Installing Python dependencies...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)Installing Dashboard dependencies...$(NC)"
	cd dashboard && $(NPM) install
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

build: ## Build Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)Build complete!$(NC)"

up: ## Start all services
	@echo "$(GREEN)Starting services...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Services started!$(NC)"
	@echo "Dashboard: http://localhost"
	@echo "API: http://localhost:8000"
	@echo "Grafana: http://localhost:3001"
	@echo "Prometheus: http://localhost:9090"

down: ## Stop all services
	@echo "$(YELLOW)Stopping services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)Services stopped!$(NC)"

restart: down up ## Restart all services

logs: ## Show logs for all services
	$(DOCKER_COMPOSE) logs -f

logs-api: ## Show API logs
	$(DOCKER_COMPOSE) logs -f api

logs-agents: ## Show agent logs
	$(DOCKER_COMPOSE) logs -f planning-agent execution-agent research-agent

logs-dashboard: ## Show dashboard logs
	$(DOCKER_COMPOSE) logs -f dashboard

ps: ## Show running containers
	$(DOCKER_COMPOSE) ps

clean: ## Clean up volumes and images
	@echo "$(RED)Warning: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_COMPOSE) down -v --rmi all; \
		echo "$(GREEN)Cleanup complete!$(NC)"; \
	fi

test: ## Run all tests
	@echo "$(GREEN)Running unit tests...$(NC)"
	pytest tests/unit -v
	@echo "$(GREEN)Running integration tests...$(NC)"
	pytest tests/integration -v
	@echo "$(GREEN)All tests passed!$(NC)"

test-unit: ## Run unit tests only
	pytest tests/unit -v

test-integration: ## Run integration tests only
	pytest tests/integration -v

test-performance: ## Run performance tests
	pytest tests/performance -v

test-coverage: ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint: ## Run linters
	@echo "$(GREEN)Running Python linters...$(NC)"
	ruff check src/ tests/
	mypy src/ --ignore-missing-imports
	@echo "$(GREEN)Running TypeScript linters...$(NC)"
	cd dashboard && npm run lint

format: ## Format code
	@echo "$(GREEN)Formatting Python code...$(NC)"
	black src/ tests/
	@echo "$(GREEN)Formatting TypeScript code...$(NC)"
	cd dashboard && npm run format

dev: ## Start development environment
	@echo "$(GREEN)Starting development environment...$(NC)"
	@trap 'kill %1 %2' INT; \
	$(PYTHON) run_api.py & \
	cd dashboard && $(NPM) run dev & \
	wait

dev-api: ## Start API in development mode
	$(PYTHON) run_api.py

dev-dashboard: ## Start dashboard in development mode
	cd dashboard && $(NPM) run dev

prod: ## Start production environment
	@echo "$(GREEN)Starting production environment...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up -d

backup: ## Backup database
	@echo "$(GREEN)Backing up database...$(NC)"
	$(DOCKER_COMPOSE) exec postgres pg_dump -U agentzero agentzero > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup complete!$(NC)"

restore: ## Restore database from backup
	@echo "$(YELLOW)Available backups:$(NC)"
	@ls -1 backup_*.sql 2>/dev/null || echo "No backups found"
	@read -p "Enter backup filename: " filename; \
	if [ -f "$$filename" ]; then \
		$(DOCKER_COMPOSE) exec -T postgres psql -U agentzero agentzero < $$filename; \
		echo "$(GREEN)Restore complete!$(NC)"; \
	else \
		echo "$(RED)File not found!$(NC)"; \
	fi

shell-api: ## Open shell in API container
	$(DOCKER_COMPOSE) exec api /bin/bash

shell-postgres: ## Open PostgreSQL shell
	$(DOCKER_COMPOSE) exec postgres psql -U agentzero agentzero

shell-redis: ## Open Redis shell
	$(DOCKER_COMPOSE) exec redis redis-cli -a changeme

monitor: ## Open monitoring dashboard
	@echo "$(GREEN)Opening monitoring dashboards...$(NC)"
	@echo "Grafana: http://localhost:3001 (admin/admin)"
	@echo "Prometheus: http://localhost:9090"
	@if command -v xdg-open > /dev/null; then \
		xdg-open http://localhost:3001; \
	elif command -v open > /dev/null; then \
		open http://localhost:3001; \
	fi

health: ## Check health of all services
	@echo "$(GREEN)Checking service health...$(NC)"
	@curl -f http://localhost:8000/health > /dev/null 2>&1 && echo "✓ API: Healthy" || echo "✗ API: Unhealthy"
	@curl -f http://localhost/health > /dev/null 2>&1 && echo "✓ Dashboard: Healthy" || echo "✗ Dashboard: Unhealthy"
	@$(DOCKER_COMPOSE) exec -T redis redis-cli ping > /dev/null 2>&1 && echo "✓ Redis: Healthy" || echo "✗ Redis: Unhealthy"
	@$(DOCKER_COMPOSE) exec -T postgres pg_isready > /dev/null 2>&1 && echo "✓ PostgreSQL: Healthy" || echo "✗ PostgreSQL: Unhealthy"

version: ## Show version information
	@echo "$(GREEN)AgentZero Version Information$(NC)"
	@echo "Project: v1.0.0"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Node: $$(node --version)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$($(DOCKER_COMPOSE) --version)"
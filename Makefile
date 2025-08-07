.PHONY: help dev prod test clean lint format install docs

# Default target
help:
	@echo "Available commands:"
	@echo "  dev          - Start development environment"
	@echo "  prod         - Start production environment"
	@echo "  build        - Build all containers"
	@echo "  test         - Run tests"
	@echo "  test-watch   - Run tests in watch mode"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  install      - Install dependencies"
	@echo "  shell        - Open shell in web container"
	@echo "  logs         - Show logs"
	@echo "  clean        - Clean up containers and volumes"
	@echo "  docs         - Start documentation server"
	@echo "  load-test    - Start load testing"
	@echo "  db-shell     - Open database shell"
	@echo "  redis-cli    - Open Redis CLI"

# Development environment
dev:
	docker compose -f docker-compose.dev.yml up -d

dev-build:
	docker compose -f docker-compose.dev.yml up --build -d

dev-logs:
	docker compose -f docker-compose.dev.yml logs -f

# Production environment
prod:
	docker compose up -d

prod-build:
	docker compose up --build -d

# Build containers
build:
	docker compose -f docker-compose.dev.yml build

# Testing
test:
	docker compose -f docker-compose.dev.yml exec web pytest

test-watch:
	docker compose -f docker-compose.dev.yml exec web pytest -f

test-cov:
	docker compose -f docker-compose.dev.yml exec web pytest --cov=src --cov-report=html

# Code quality
lint:
	docker compose -f docker-compose.dev.yml exec web pre-commit run --all-files

format:
	docker compose -f docker-compose.dev.yml exec web black .
	docker compose -f docker-compose.dev.yml exec web isort .

mypy:
	docker compose -f docker-compose.dev.yml exec web mypy src

# Dependencies
install:
	docker compose -f docker-compose.dev.yml exec web pip install -r requirements-dev.txt

# Shell access
shell:
	docker compose -f docker-compose.dev.yml exec web bash

web-shell: shell

db-shell:
	docker compose -f docker-compose.dev.yml exec db psql -U postgres -d newsdb_dev

redis-cli:
	docker compose -f docker-compose.dev.yml exec redis redis-cli

# Logs
logs:
	docker compose -f docker-compose.dev.yml logs -f

web-logs:
	docker compose -f docker-compose.dev.yml logs -f web

db-logs:
	docker compose -f docker-compose.dev.yml logs -f db

# Documentation
docs:
	docker compose -f docker-compose.dev.yml --profile docs up -d docs

docs-build:
	docker compose -f docker-compose.dev.yml exec web mkdocs build

# Load testing
load-test:
	docker compose -f docker-compose.dev.yml --profile load-test up -d locust

# Database operations
db-migrate:
	docker compose -f docker-compose.dev.yml exec web alembic upgrade head

db-reset:
	docker compose -f docker-compose.dev.yml exec web alembic downgrade base
	docker compose -f docker-compose.dev.yml exec web alembic upgrade head

# Cleanup
clean:
	docker compose -f docker-compose.dev.yml down -v
	docker system prune -f

clean-all: clean
	docker-compose down -v
	docker system prune -af

stop:
	docker compose -f docker-compose.dev.yml stop

down:
	docker compose -f docker-compose.dev.yml down

# Restart services
restart:
	docker compose -f docker-compose.dev.yml restart

restart-web:
	docker compose -f docker-compose.dev.yml restart web

# Health checks
health:
	docker compose -f docker-compose.dev.yml exec web curl -f http://localhost:8000/health || exit 1

# Pre-commit hooks
pre-commit-install:
	docker compose -f docker-compose.dev.yml exec web pre-commit install

pre-commit-run:
	docker compose -f docker-compose.dev.yml exec web pre-commit run --all-files

# Security checks
security:
	docker compose -f docker-compose.dev.yml exec web bandit -r src
	docker compose -f docker-compose.dev.yml exec web safety check

# Performance profiling
profile:
	docker compose -f docker-compose.dev.yml exec web py-spy top --pid 1

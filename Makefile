.PHONY: help build up down restart logs test visualize clean

help:  ## Show this help message
	@echo "Sumble Advanced Query API - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

build:  ## Build Docker containers
	docker compose build

up:  ## Start all services (db + api)
	docker compose up -d
	@echo "✅ Services started"
	@echo "📍 API: http://localhost:8000"
	@echo "📚 Docs: http://localhost:8000/docs"

down:  ## Stop all services
	docker compose down
	@echo "✅ Services stopped"

restart:  ## Restart all services
	docker compose down
	docker compose up -d
	@echo "✅ Services restarted"

logs:  ## View API logs
	docker compose logs -f api

logs-db:  ## View database logs
	docker compose logs -f db

test:  ## Run comprehensive test suite
	@echo "Running test suite..."
	@source venv/bin/activate && python tests/test_queries.py

visualize:  ## Visualize test results
	@echo "Generating performance dashboard..."
	@source venv/bin/activate && python scripts/visualize_results.py

setup:  ## Initial setup (venv + dependencies)
	python3.12 -m venv venv
	@echo "✅ Virtual environment created"
	@echo "Run: source venv/bin/activate && pip install -r requirements.txt"

install:  ## Install Python dependencies
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

clean:  ## Clean up generated files
	rm -rf reports/test_results.json
	rm -rf app/__pycache__
	rm -rf tests/__pycache__
	rm -rf scripts/__pycache__
	@echo "✅ Cleaned up generated files"

clean-all:  ## Clean everything including Docker volumes
	docker compose down -v
	rm -rf reports/test_results.json
	rm -rf app/__pycache__
	rm -rf tests/__pycache__
	rm -rf scripts/__pycache__
	@echo "✅ Cleaned everything"

status:  ## Check service status
	@echo "Docker Services:"
	@docker compose ps
	@echo ""
	@echo "API Health:"
	@curl -s http://localhost:8000/api/v1/health | python -m json.tool || echo "API not running"

shell-api:  ## Open shell in API container
	docker compose exec api /bin/bash

shell-db:  ## Open psql in database container
	docker compose exec db psql -U postgres -d sumble_data

dev:  ## Start services and show logs
	docker compose up --build


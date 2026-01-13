.PHONY: up down build logs backend-shell mysql-shell init-db

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

backend-shell:
	docker-compose exec backend bash

init-db:
	docker-compose exec backend alembic upgrade head

format:
	cd backend && ruff format .
	cd frontend && npm run format

test:
	cd backend && pytest

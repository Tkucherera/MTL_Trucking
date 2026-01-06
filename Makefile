.PHONY: help build up down logs migrate test clean

help:
	@echo "Available commands:"
	@echo "  make build        - Build Docker images"
	@echo "  make up           - Start containers"
	@echo "  make down         - Stop containers"
	@echo "  make logs         - View logs"
	@echo "  make migrate      - Run Django migrations"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean up Docker resources"
	@echo "  make prod-build   - Build production images"
	@echo "  make prod-up      - Start production containers"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	docker-compose exec backend python manage.py migrate

makemigrations:
	docker-compose exec backend python manage.py makemigrations

test:
	docker-compose exec backend python manage.py test
	docker-compose exec frontend npm test

clean:
	docker-compose down -v
	docker system prune -f

prod-build:
	docker compose -f docker-compose.prod.yml build

prod-up:
	docker compose -f docker-compose.prod.yml up -d

prod-down:
	docker compose -f docker-compose.prod.yml down

prod-logs:
	docker compose -f docker-compose.prod.yml logs -f

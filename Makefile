.PHONY: install dev test lint typecheck migrate seed admin docker-up docker-down

install:
	pip install -r requirements-dev.txt

dev:
	uvicorn app.main:app --reload

test:
	pytest -q --cov=app --cov-report=term-missing

lint:
	ruff check app tests scripts

typecheck:
	mypy app

migrate:
	alembic upgrade head

seed:
	python scripts/seed_database.py

admin:
	python scripts/create_admin.py

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v

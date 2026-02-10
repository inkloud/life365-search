.PHONY: help venv test api-up lint clean docker-up docker-down upgrade

help:
	@echo "Targets: venv test api-up lint clean docker-up docker-down upgrade"

venv:
	uv venv
	uv pip sync requirements.txt
	rm .venv/.gitignore

test:
	uv run pytest

api-up:
	uv run uvicorn app.main:app --reload

lint:
	uv run ruff check .

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	rm -f uv.lock

docker-up:
	docker compose up

docker-down:
	docker compose down -v
	docker image prune -a

upgrade:
	rm -f requirements.txt
	uv venv
	uv pip compile requirements.in > requirements.txt
	rm .venv/.gitignore

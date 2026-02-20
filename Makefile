.PHONY: venv test api-up clean docker-up docker-down upgrade

export USER_ID := $(shell id -u)
export GROUP_ID := $(shell id -g)

SHARED_NETWORK := life365-shared

upgrade:
	rm -f requirements.txt
	uv venv
	uv pip compile requirements.in > requirements.txt
	uv pip sync requirements.txt
	rm .venv/.gitignore

venv:
	uv venv
	uv pip sync requirements.txt
	rm .venv/.gitignore

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	rm -f uv.lock

test:
	uv run pytest

api-up:
	uv run uvicorn app.main:app --reload

docker-up:
	docker network inspect $(SHARED_NETWORK) >/dev/null 2>&1 || docker network create $(SHARED_NETWORK)
	docker compose up

docker-down:
	docker compose down -v
	docker network rm $(SHARED_NETWORK) >/dev/null 2>&1 || true
	docker image prune -a
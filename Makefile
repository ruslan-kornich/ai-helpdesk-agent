.PHONY: run down report seed test build create-user

run:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

report:
	docker compose exec app uv run python -m app.cli report

seed:
	docker compose exec app uv run python -m app.seed

create-user:
	docker compose exec app uv run python -m app.create_user

test:
	cd backend && uv run pytest -v

.PHONY: install lint test demo ui

install:
	uv sync

lint:
	uv run ruff check tools/ tests/ tickets/ app.py

test:
	uv run pytest -v

demo:
	uv run python tools/ticket_prioritizer.py
	uv run python tools/rule_generator.py
	uv run python tools/diagnostic_helper.py --family notification --component "Webhook Bridge"

ui:
	uv run python app.py

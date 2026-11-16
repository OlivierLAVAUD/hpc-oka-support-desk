.PHONY: install lint test demo ui contracts llm-check

install:
	uv sync

lint:
	uv run ruff check tools/ tests/ tickets/ app.py interface_cli.py

test:
	uv run pytest -v

demo:
	uv run python tools/ticket_prioritizer.py
	uv run python tools/rule_generator.py
	uv run python tools/diagnostic_helper.py --family notification --component "Webhook Bridge"

contracts:
	uv run python -m tools.contract_context

llm-check:
	uv run python -m tools.llm_client --check

ui:
	uv run python app.py

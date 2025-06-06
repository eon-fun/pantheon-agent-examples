.PHONY: run-locally	test

export PYTHONPATH := $(shell pwd)/src
export ENV_FILE := .env

run-locally:
	@echo "Running FastAPI app locally with .env loaded..."
	env $$(cat .env | xargs) python entrypoint.py

test:
	@if [ -d ./tests ] && ls ./tests/test*.py 1>/dev/null 2>&1; then \
		echo "✅ Running tests..."; \
		ENVIRONMENT=test pytest -v; \
	else \
		echo "⚠️  No tests to run."; \
	fi
	
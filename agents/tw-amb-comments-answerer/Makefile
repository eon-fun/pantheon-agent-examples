.PHONY: test

export PYTHONPATH := $(shell pwd)/src
export ENV_FILE := .env

test:
	@if [ -d ./tests ] && ls ./tests/test*.py 1>/dev/null 2>&1; then \
		echo "✅ Running tests..."; \
		ENVIRONMENT=test pytest -v; \
	else \
		echo "⚠️  No tests to run."; \
	fi
	
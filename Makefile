.PHONY: up down venv java haskell test all clean wait-pg

# Load .env if it exists
-include .env
export

PROJECT_ROOT := $(shell pwd)
VENV         := $(PROJECT_ROOT)/tests/.venv
PIP          := $(VENV)/bin/pip
PYTEST       := $(VENV)/bin/pytest

# Defaults (overridden by .env if present)
DB_HOST     ?= localhost
DB_PORT     ?= 5432
DB_NAME     ?= meteorological
DB_USER     ?= meteo
DB_PASSWORD ?= meteo123
CSV_PATH    ?= test.csv

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

up:
	docker compose up -d

down:
	docker compose down -v

wait-pg:
	@echo "Waiting for PostgreSQL to be ready..."
	@until docker compose exec -T postgres pg_isready -U $(DB_USER) -d $(DB_NAME) > /dev/null 2>&1; do \
		sleep 1; \
	done
	@echo "PostgreSQL is ready."

# ---------------------------------------------------------------------------
# Python venv
# ---------------------------------------------------------------------------

venv: $(VENV)/bin/activate

$(VENV)/bin/activate: tests/requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r tests/requirements.txt
	touch $(VENV)/bin/activate

# ---------------------------------------------------------------------------
# ETL implementations
# ---------------------------------------------------------------------------

java:
	cd java-etl && export JAVA_HOME=/usr/lib/jvm/java-21-amazon-corretto && export PATH="$JAVA_HOME/bin:$PATH" && hash -r && mvn -q compile exec:java

haskell:
	cd haskell-etl && stack run

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

test: venv
	$(PYTEST) tests/ -v

# ---------------------------------------------------------------------------
# All-in-one
# ---------------------------------------------------------------------------

all: up wait-pg java haskell test

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean: down
	rm -rf java-etl/target
	rm -rf haskell-etl/.stack-work
	rm -rf tests/.venv
	rm -rf tests/__pycache__
	rm -rf tests/.pytest_cache

# Meteorological ETL — Java vs Haskell Comparison

A master's thesis project comparing OOP (Java) and functional (Haskell) implementations of the same ETL pipeline for meteorological data.

## Prerequisites

- Docker & Docker Compose
- Java 21 + Maven
- GHC + Stack (Haskell)
- Python 3.12+

## Configuration

All settings are managed through environment variables. Copy the example file and adjust as needed:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `meteorological` | Database name |
| `DB_USER` | `meteo` | Database user |
| `DB_PASSWORD` | `meteo123` | Database password |
| `CSV_PATH` | `test.csv` | Path to source CSV (relative to project root) |

The `.env` file is loaded by the Makefile and docker-compose automatically. Each ETL implementation also reads these variables at runtime (falling back to the defaults above).

## Quick Start

```bash
# 1. Configure (or just use defaults)
cp .env.example .env

# 2. Start PostgreSQL
make up

# 3. Set up Python test environment
make venv

# 4. Run both ETLs and tests
make all
```

## Individual Commands

```bash
make up          # Start PostgreSQL container
make wait-pg     # Wait until PostgreSQL is ready
make java        # Build and run Java ETL
make haskell     # Build and run Haskell ETL
make test        # Run pytest verification suite
make down        # Stop and remove containers + volumes
make clean       # Full cleanup (containers, build artifacts, venv)
```

## Project Structure

```
.
├── .env.example                # Environment variable defaults (copy to .env)
├── docker-compose.yml          # PostgreSQL 16 service
├── init/
│   └── 01-create-table.sql     # DB schema (auto-run on first start)
├── test.csv                    # Source meteorological data (imperial units)
├── java-etl/                   # Java/Maven ETL implementation
│   ├── pom.xml
│   └── src/main/java/br/edu/utfpr/etl/
│       ├── Main.java
│       ├── WeatherRecord.java
│       ├── CsvExtractor.java
│       ├── Transformer.java
│       ├── UnitConverter.java
│       └── DatabaseLoader.java
├── haskell-etl/                # Haskell/Stack ETL implementation
│   ├── stack.yaml
│   ├── meteo-etl.cabal
│   └── src/
│       ├── Main.hs
│       ├── WeatherRecord.hs
│       ├── CsvExtractor.hs
│       ├── Transformer.hs
│       ├── UnitConverter.hs
│       └── DatabaseLoader.hs
├── tests/                      # pytest + psycopg3 verification suite
│   ├── requirements.txt
│   ├── conftest.py
│   ├── test_etl.py             # Per-implementation tests (parametrized)
│   └── test_cross_impl.py      # Cross-implementation equivalence test
├── Makefile                    # Build/run/test orchestration
├── projeto.md                  # Project specification + data model
└── plan.md                     # Implementation plan
```

## Unit Conversions

All imperial values from the CSV are converted to metric before database insert:

| Conversion | Formula |
|---|---|
| Fahrenheit → Celsius | `(F − 32) × 5 / 9` |
| Inches → Millimeters | `value × 25.4` |
| Miles/h → Km/h | `value × 1.60934` |
| Miles → Km | `value × 1.60934` |

All converted floats are rounded to **2 decimal places**.

## Test Strategy

Tests use **pytest** with **psycopg3** to query the database after each ETL run:

- **Row count**: exactly 15 rows loaded
- **Schema**: all 33 columns present with correct types
- **Value equivalence**: each value matches Python-computed golden data (`pytest.approx` for floats)
- **Null handling**: empty CSV fields stored as SQL `NULL`
- **Cross-implementation**: Java and Haskell outputs are row-by-row identical

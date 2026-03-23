# Plan: Dual-Language Meteorological ETL Implementation

Implement the same meteorological ETL pipeline in **Java** (Maven) and **Haskell** (Stack), reading weather CSV data, converting all imperial units to metric (rounded to 2 decimal places), and loading into a Dockerized PostgreSQL — with a **pytest + psycopg3** test suite verifying both implementations produce identical results. Orchestrated via a top-level **Makefile**.

---

## Steps

### 1. Create Docker Infrastructure

Write a `docker-compose.yml` at the project root with a PostgreSQL 16 service:
- Mount an `init/` directory for automatic startup SQL scripts
- Expose port `5432`
- Set database name, user, and password via environment variables

### 2. Write the DB Init Script

Add `init/01-create-table.sql` creating the `meteorological_data` table with all 33 columns stored in metric units:

| Column | Type | Unit | Conversion |
|---|---|---|---|
| `name` | `TEXT` | — | none |
| `datetime` | `DATE` | — | none |
| `tempmax`, `tempmin`, `temp`, `feelslikemax`, `feelslikemin`, `feelslike`, `dew` | `REAL` | °C | `(F − 32) × 5/9` |
| `humidity`, `precipprob`, `precipcover` | `REAL` | % | none (already metric) |
| `precip` | `REAL` | mm | `× 25.4` |
| `preciptype` | `TEXT NULL` | — | none |
| `snow` | `REAL NULL` | mm | `× 25.4` |
| `snowdepth` | `REAL NULL` | mm | `× 25.4` |
| `windgust`, `windspeed` | `REAL` | km/h | `× 1.60934` |
| `winddir` | `REAL` | degrees | none (already metric) |
| `sealevelpressure` | `REAL` | hPa | none (hPa = mbar, already metric) |
| `cloudcover` | `REAL` | % | none (already metric) |
| `visibility` | `REAL` | km | `× 1.60934` |
| `solarradiation` | `REAL` | W/m² | none (already metric) |
| `solarenergy` | `REAL` | MJ/m² | none (already metric) |
| `uvindex` | `REAL` | index | none |
| `severerisk` | `REAL` | index | none |
| `sunrise`, `sunset` | `TIMESTAMP` | — | none |
| `moonphase` | `REAL` | 0–1 | none |
| `conditions`, `description`, `icon` | `TEXT` | — | none |
| `stations` | `TEXT NULL` | — | none |

### 3. Define the Shared Data Model

Add a section to `projeto.md` documenting the canonical data model:
- All field names and SQL types
- Metric units and conversion formulas
- 2-decimal rounding rule for all converted float values
- Nullability rules: `preciptype`, `snow`, `snowdepth`, `stations` can be NULL (empty CSV = NULL)

### 4. Implement the Java ETL (`java-etl/`, Maven)

- `WeatherRecord` Java record mirroring the data model with `Optional<String>` / `Optional<Double>` for nullable fields
- CSV reader using OpenCSV parsing `test.csv` into `WeatherRecord` instances
- Transform step applying all unit conversions:
  - 7 temperature fields: `(F − 32) × 5/9`
  - `precip`, `snow`, `snowdepth`: `× 25.4`
  - `windgust`, `windspeed`, `visibility`: `× 1.60934`
  - All rounded to 2 decimal places via `Math.round(v * 100.0) / 100.0`
- JDBC batch loader using `PreparedStatement`, calling `setNull()` for `Optional.empty()` values
- `Main` class orchestrating Extract → Transform → Load

### 5. Implement the Haskell ETL (`haskell-etl/`, Stack)

- `WeatherRecord` algebraic data type with `Maybe Text` / `Maybe Double` for nullable fields
- CSV decoder using `cassava` parsing `test.csv` into `WeatherRecord` values
- Transform step applying the same unit conversions, rounded via `fromIntegral (round (v * 100)) / 100`
- PostgreSQL loader using `postgresql-simple`, mapping `Nothing` to SQL `NULL`
- `Main` module orchestrating Extract → Transform → Load

### 6. Set Up the Python Test Environment (`tests/`)

- `tests/requirements.txt` with `pytest` and `psycopg[binary]`
- Python venv at `tests/.venv/`
- `tests/.venv/` added to `.gitignore`
- Venv creation handled by Makefile `venv` target

### 7. Create the Pytest Verification Suite (`tests/`)

- **`tests/conftest.py`**:
  - Session-scoped `psycopg.Connection` fixture connected to the Dockerized PostgreSQL
  - `run_etl(impl)` helper: truncates `meteorological_data`, runs ETL via `subprocess.run()` (`mvn -f java-etl exec:java` or `cd haskell-etl && stack run`)
  - Golden data fixture: reads `test.csv` in Python, applies the same 13 conversions + 2-decimal round, returns expected rows as list of dicts

- **`tests/test_etl.py`** — parametrized by `["java", "haskell"]`:
  - **Row count**: `SELECT COUNT(*)` = 15
  - **Schema check**: verify all 33 columns exist with correct types via `information_schema.columns`
  - **Value equivalence**: `SELECT * ... ORDER BY datetime` matches golden data (`pytest.approx(abs=0.01)` for floats, exact for strings/dates)
  - **Null handling**: nullable columns are `None` where CSV has empty values

- **`tests/test_cross_impl.py`**:
  - Run Java ETL (truncate → load → fetch all rows into memory)
  - Run Haskell ETL (truncate → load → fetch all rows into memory)
  - Assert row-by-row equivalence between both using `pytest.approx()`

### 8. Add a Makefile

Top-level `Makefile` with targets:
- `up` — `docker compose up -d`
- `down` — `docker compose down -v`
- `venv` — create Python venv and install test dependencies
- `java` — build and run Java ETL
- `haskell` — build and run Haskell ETL
- `test` — run pytest suite
- `all` — `up`, wait for PG ready, `java`, `haskell`, `test`
- `clean` — `down`, remove build artifacts

### 9. Add a README

Describe full workflow: `make up` → `make venv` → `make all` or individual targets. Outline thesis comparison axes (readability, LOC, performance, library footprint).

---

## Important Notes

- **Floating-point precision**: all converted values rounded to 2 decimal places in both implementations before DB insert. Tests use `pytest.approx(abs=0.01)`.
- **Empty string = NULL**: empty CSV fields for `preciptype`, `snow`, `snowdepth`, `stations` must be stored as SQL `NULL`, never as empty string.
- **`sealevelpressure`**: hPa and mbar are numerically identical — no conversion needed.
- **Test isolation**: each test parametrization truncates the table before running its ETL, ensuring identical starting state.

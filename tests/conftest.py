import csv
import subprocess
import math
import os
from datetime import date, datetime
from pathlib import Path

import psycopg
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / os.environ.get("CSV_PATH", "test-small.csv")

DB_PARAMS = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", "5432")),
    "dbname": os.environ.get("DB_NAME", "meteorological"),
    "user": os.environ.get("DB_USER", "meteo"),
    "password": os.environ.get("DB_PASSWORD", "meteo123"),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def round2(value: float) -> float:
    """Round to 2 decimal places, matching Java/Haskell rounding."""
    return math.floor(value * 100.0 + 0.5) / 100.0


def f_to_c(f: float) -> float:
    return round2((f - 32.0) * 5.0 / 9.0)


def inches_to_mm(v: float) -> float:
    return round2(v * 25.4)


def miles_to_km(v: float) -> float:
    return round2(v * 1.60934)


def parse_optional_float(val: str):
    val = val.strip()
    return None if val == "" else float(val)


def parse_optional_str(val: str):
    val = val.strip()
    return None if val == "" else val


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def db_conn():
    """Session-scoped PostgreSQL connection."""
    conn = psycopg.connect(**DB_PARAMS)
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def golden_data():
    """Expected rows after metric conversion, computed from CSV in Python."""
    rows = []
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            snow_raw = parse_optional_float(row["snow"])
            snowdepth_raw = parse_optional_float(row["snowdepth"])

            record = {
                "name": row["name"],
                "datetime": date.fromisoformat(row["datetime"]),
                "tempmax": f_to_c(float(row["tempmax"])),
                "tempmin": f_to_c(float(row["tempmin"])),
                "temp": f_to_c(float(row["temp"])),
                "feelslikemax": f_to_c(float(row["feelslikemax"])),
                "feelslikemin": f_to_c(float(row["feelslikemin"])),
                "feelslike": f_to_c(float(row["feelslike"])),
                "dew": f_to_c(float(row["dew"])),
                "humidity": float(row["humidity"]),
                "precip": inches_to_mm(float(row["precip"])),
                "precipprob": float(row["precipprob"]),
                "precipcover": float(row["precipcover"]),
                "preciptype": parse_optional_str(row["preciptype"]),
                "snow": inches_to_mm(snow_raw) if snow_raw is not None else None,
                "snowdepth": inches_to_mm(snowdepth_raw) if snowdepth_raw is not None else None,
                "windgust": miles_to_km(float(row["windgust"])),
                "windspeed": miles_to_km(float(row["windspeed"])),
                "winddir": float(row["winddir"]),
                "sealevelpressure": float(row["sealevelpressure"]),
                "cloudcover": float(row["cloudcover"]),
                "visibility": miles_to_km(float(row["visibility"])),
                "solarradiation": float(row["solarradiation"]),
                "solarenergy": float(row["solarenergy"]),
                "uvindex": float(row["uvindex"]),
                "severerisk": float(row["severerisk"]),
                "sunrise": datetime.fromisoformat(row["sunrise"]),
                "sunset": datetime.fromisoformat(row["sunset"]),
                "moonphase": float(row["moonphase"]),
                "conditions": row["conditions"],
                "description": row["description"],
                "icon": row["icon"],
                "stations": parse_optional_str(row["stations"]),
            }
            rows.append(record)
    return rows


def run_etl(impl: str, conn):
    """Truncate table and run an ETL implementation."""
    with conn.cursor() as cur:
        cur.execute("TRUNCATE meteorological_data RESTART IDENTITY")
    conn.commit()

    if impl == "java":
        subprocess.run(
            ["mvn", "-f", str(PROJECT_ROOT / "java-etl"), "compile", "exec:java"],
            cwd=str(PROJECT_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
    elif impl == "haskell":
        subprocess.run(
            ["stack", "run"],
            cwd=str(PROJECT_ROOT / "haskell-etl"),
            check=True,
            capture_output=True,
            text=True,
        )
    else:
        raise ValueError(f"Unknown implementation: {impl}")


def fetch_all_rows(conn):
    """Fetch all rows ordered by datetime."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT name, datetime, tempmax, tempmin, temp, "
            "feelslikemax, feelslikemin, feelslike, dew, "
            "humidity, precip, precipprob, precipcover, preciptype, "
            "snow, snowdepth, windgust, windspeed, winddir, "
            "sealevelpressure, cloudcover, visibility, "
            "solarradiation, solarenergy, uvindex, severerisk, "
            "sunrise, sunset, moonphase, "
            "conditions, description, icon, stations "
            "FROM meteorological_data ORDER BY datetime"
        )
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

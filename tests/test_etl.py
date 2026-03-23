import pytest
from conftest import run_etl, fetch_all_rows


FLOAT_COLUMNS = [
    "tempmax", "tempmin", "temp", "feelslikemax", "feelslikemin", "feelslike",
    "dew", "humidity", "precip", "precipprob", "precipcover",
    "windgust", "windspeed", "winddir", "sealevelpressure", "cloudcover",
    "visibility", "solarradiation", "solarenergy", "uvindex", "severerisk",
    "moonphase",
]

NULLABLE_COLUMNS = ["preciptype", "snow", "snowdepth", "stations"]

ALL_COLUMNS = [
    "name", "datetime", "tempmax", "tempmin", "temp",
    "feelslikemax", "feelslikemin", "feelslike", "dew",
    "humidity", "precip", "precipprob", "precipcover", "preciptype",
    "snow", "snowdepth", "windgust", "windspeed", "winddir",
    "sealevelpressure", "cloudcover", "visibility",
    "solarradiation", "solarenergy", "uvindex", "severerisk",
    "sunrise", "sunset", "moonphase",
    "conditions", "description", "icon", "stations",
]


@pytest.mark.parametrize("impl", ["java", "haskell"])
class TestEtl:

    def test_row_count(self, impl, db_conn, golden_data):
        """Each implementation should load exactly 15 rows."""
        run_etl(impl, db_conn)
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM meteorological_data")
            count = cur.fetchone()[0]
        assert count == len(golden_data), f"{impl}: expected {len(golden_data)} rows, got {count}"

    def test_schema_columns(self, impl, db_conn):
        """All 33 data columns must exist."""
        run_etl(impl, db_conn)
        with db_conn.cursor() as cur:
            cur.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'meteorological_data' "
                "AND table_schema = 'public' "
                "ORDER BY ordinal_position"
            )
            db_columns = [row[0] for row in cur.fetchall()]

        # 'id' is auto-generated, the rest should match
        for col in ALL_COLUMNS:
            assert col in db_columns, f"{impl}: missing column '{col}'"

    def test_value_equivalence(self, impl, db_conn, golden_data):
        """All values must match the golden data."""
        run_etl(impl, db_conn)
        actual_rows = fetch_all_rows(db_conn)

        assert len(actual_rows) == len(golden_data), (
            f"{impl}: row count mismatch {len(actual_rows)} vs {len(golden_data)}"
        )

        for i, (actual, expected) in enumerate(zip(actual_rows, golden_data)):
            for col in ALL_COLUMNS:
                actual_val = actual[col]
                expected_val = expected[col]

                if expected_val is None:
                    assert actual_val is None, (
                        f"{impl} row {i} col '{col}': expected NULL, got {actual_val}"
                    )
                elif col in FLOAT_COLUMNS or col in ("snow", "snowdepth"):
                    assert actual_val == pytest.approx(expected_val, abs=0.01), (
                        f"{impl} row {i} col '{col}': {actual_val} != {expected_val}"
                    )
                else:
                    assert actual_val == expected_val, (
                        f"{impl} row {i} col '{col}': {actual_val!r} != {expected_val!r}"
                    )

    def test_null_handling(self, impl, db_conn, golden_data):
        """Nullable columns should be NULL where CSV is empty."""
        run_etl(impl, db_conn)
        actual_rows = fetch_all_rows(db_conn)

        for i, (actual, expected) in enumerate(zip(actual_rows, golden_data)):
            for col in NULLABLE_COLUMNS:
                if expected[col] is None:
                    assert actual[col] is None, (
                        f"{impl} row {i} col '{col}': expected NULL, got {actual[col]!r}"
                    )
                else:
                    assert actual[col] is not None, (
                        f"{impl} row {i} col '{col}': expected value, got NULL"
                    )

import pytest
from conftest import run_etl, fetch_all_rows


FLOAT_COLUMNS = [
    "tempmax", "tempmin", "temp", "feelslikemax", "feelslikemin", "feelslike",
    "dew", "humidity", "precip", "precipprob", "precipcover",
    "snow", "snowdepth",
    "windgust", "windspeed", "winddir", "sealevelpressure", "cloudcover",
    "visibility", "solarradiation", "solarenergy", "uvindex", "severerisk",
    "moonphase",
]

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


class TestCrossImplementation:

    def test_java_and_haskell_produce_identical_results(self, db_conn):
        """Both implementations must produce exactly the same database output."""
        # Run Java ETL and capture rows
        run_etl("java", db_conn)
        java_rows = fetch_all_rows(db_conn)

        # Run Haskell ETL and capture rows
        run_etl("haskell", db_conn)
        haskell_rows = fetch_all_rows(db_conn)

        assert len(java_rows) == len(haskell_rows), (
            f"Row count mismatch: Java={len(java_rows)}, Haskell={len(haskell_rows)}"
        )

        for i, (j_row, h_row) in enumerate(zip(java_rows, haskell_rows)):
            for col in ALL_COLUMNS:
                j_val = j_row[col]
                h_val = h_row[col]

                if j_val is None and h_val is None:
                    continue
                elif j_val is None or h_val is None:
                    pytest.fail(
                        f"Row {i} col '{col}': Java={j_val!r}, Haskell={h_val!r} "
                        "(one is NULL, the other is not)"
                    )
                elif col in FLOAT_COLUMNS:
                    assert j_val == pytest.approx(h_val, abs=0.01), (
                        f"Row {i} col '{col}': Java={j_val}, Haskell={h_val}"
                    )
                else:
                    assert j_val == h_val, (
                        f"Row {i} col '{col}': Java={j_val!r}, Haskell={h_val!r}"
                    )

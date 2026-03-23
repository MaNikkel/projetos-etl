# Context
This is the practical project for my masters, it is the comparison of a OOP language (Java) and a functional programming language (Haskell). The aim is to implement the same project in both languages and compare the results, in terms of code readability, maintainability, performance and other factors that may be relevant.

The subject here is a simple ETL for meteorological data, the data is in a CSV format and contains information about the temperature, humidity, pressure and other meteorological variables. The ETL process will consist of reading the data from the CSV file, transforming it into a suitable format for analysis and then loading it into a Postgres database.

# Implementation
1. gather data from test.csv file
2. write a docker-compose file to run a Postgres database
3. create a table in the Postgres database to store the meteorological data, this has to be reproducible, so it should be done through a SQL script, better if it is done through the init folder of the Postgres docker image
4. Create a common model for the meteorological data, this model should be used in both implementations (Java and Haskell)
5. Implement the ETL process in Java, the less additional libraries the better, but it is allowed to use libraries for reading CSV files and for connecting to the Postgres database
6. Implement the ETL process in Haskell, the less additional libraries the better, but it is allowed to use libraries for reading CSV files and for connecting to the Postgres database

# Data Model

All values are stored in metric units. Imperial fields from the CSV are converted before insert.
All converted float values are rounded to 2 decimal places.
Empty CSV fields for nullable columns are stored as SQL `NULL`.

## Columns

| Column | SQL Type | Unit | Conversion from CSV |
|---|---|---|---|
| `name` | `TEXT NOT NULL` | — | none |
| `datetime` | `DATE NOT NULL` | — | none |
| `tempmax` | `REAL NOT NULL` | °C | `(F − 32) × 5/9` |
| `tempmin` | `REAL NOT NULL` | °C | `(F − 32) × 5/9` |
| `temp` | `REAL NOT NULL` | °C | `(F − 32) × 5/9` |
| `feelslikemax` | `REAL NOT NULL` | °C | `(F − 32) × 5/9` |
| `feelslikemin` | `REAL NOT NULL` | °C | `(F − 32) × 5/9` |
| `feelslike` | `REAL NOT NULL` | °C | `(F − 32) × 5/9` |
| `dew` | `REAL NOT NULL` | °C | `(F − 32) × 5/9` |
| `humidity` | `REAL NOT NULL` | % | none |
| `precip` | `REAL NOT NULL` | mm | `× 25.4` |
| `precipprob` | `REAL NOT NULL` | % | none |
| `precipcover` | `REAL NOT NULL` | % | none |
| `preciptype` | `TEXT NULL` | — | none (empty → NULL) |
| `snow` | `REAL NULL` | mm | `× 25.4` (empty → NULL) |
| `snowdepth` | `REAL NULL` | mm | `× 25.4` (empty → NULL) |
| `windgust` | `REAL NOT NULL` | km/h | `× 1.60934` |
| `windspeed` | `REAL NOT NULL` | km/h | `× 1.60934` |
| `winddir` | `REAL NOT NULL` | degrees | none |
| `sealevelpressure` | `REAL NOT NULL` | hPa | none (hPa = mbar) |
| `cloudcover` | `REAL NOT NULL` | % | none |
| `visibility` | `REAL NOT NULL` | km | `× 1.60934` |
| `solarradiation` | `REAL NOT NULL` | W/m² | none |
| `solarenergy` | `REAL NOT NULL` | MJ/m² | none |
| `uvindex` | `REAL NOT NULL` | index | none |
| `severerisk` | `REAL NOT NULL` | index | none |
| `sunrise` | `TIMESTAMP NOT NULL` | — | none |
| `sunset` | `TIMESTAMP NOT NULL` | — | none |
| `moonphase` | `REAL NOT NULL` | 0–1 | none |
| `conditions` | `TEXT NOT NULL` | — | none |
| `description` | `TEXT NOT NULL` | — | none |
| `icon` | `TEXT NOT NULL` | — | none |
| `stations` | `TEXT NULL` | — | none (empty → NULL) |

## Conversion Formulas

- **Fahrenheit → Celsius**: `(value − 32) × 5 / 9`
- **Inches → Millimeters**: `value × 25.4`
- **Miles/h → Km/h**: `value × 1.60934`
- **Miles → Km**: `value × 1.60934`
- **Rounding**: `round(value × 100) / 100` (2 decimal places)

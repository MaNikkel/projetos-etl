package br.edu.utfpr.etl;

import java.sql.*;
import java.util.List;

public class DatabaseLoader {

    private static final String INSERT_SQL = """
        INSERT INTO meteorological_data (
            name, datetime, tempmax, tempmin, temp,
            feelslikemax, feelslikemin, feelslike, dew,
            humidity, precip, precipprob, precipcover, preciptype,
            snow, snowdepth, windgust, windspeed, winddir,
            sealevelpressure, cloudcover, visibility,
            solarradiation, solarenergy, uvindex, severerisk,
            sunrise, sunset, moonphase,
            conditions, description, icon, stations
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?
        )
        """;

    private final String jdbcUrl;
    private final String user;
    private final String password;

    public DatabaseLoader(String jdbcUrl, String user, String password) {
        this.jdbcUrl = jdbcUrl;
        this.user = user;
        this.password = password;
    }

    public void load(List<WeatherRecord> records) throws SQLException {
        try (Connection conn = DriverManager.getConnection(jdbcUrl, user, password);
             PreparedStatement ps = conn.prepareStatement(INSERT_SQL)) {

            conn.setAutoCommit(false);

            for (WeatherRecord r : records) {
                int idx = 1;
                ps.setString(idx++, r.name());
                ps.setDate(idx++, Date.valueOf(r.datetime()));
                ps.setDouble(idx++, r.tempmax());
                ps.setDouble(idx++, r.tempmin());
                ps.setDouble(idx++, r.temp());
                ps.setDouble(idx++, r.feelslikemax());
                ps.setDouble(idx++, r.feelslikemin());
                ps.setDouble(idx++, r.feelslike());
                ps.setDouble(idx++, r.dew());
                ps.setDouble(idx++, r.humidity());
                ps.setDouble(idx++, r.precip());
                ps.setDouble(idx++, r.precipprob());
                ps.setDouble(idx++, r.precipcover());

                if (r.preciptype().isPresent()) {
                    ps.setString(idx++, r.preciptype().get());
                } else {
                    ps.setNull(idx++, Types.VARCHAR);
                }

                if (r.snow().isPresent()) {
                    ps.setDouble(idx++, r.snow().get());
                } else {
                    ps.setNull(idx++, Types.REAL);
                }

                if (r.snowdepth().isPresent()) {
                    ps.setDouble(idx++, r.snowdepth().get());
                } else {
                    ps.setNull(idx++, Types.REAL);
                }

                ps.setDouble(idx++, r.windgust());
                ps.setDouble(idx++, r.windspeed());
                ps.setDouble(idx++, r.winddir());
                ps.setDouble(idx++, r.sealevelpressure());
                ps.setDouble(idx++, r.cloudcover());
                ps.setDouble(idx++, r.visibility());
                ps.setDouble(idx++, r.solarradiation());
                ps.setDouble(idx++, r.solarenergy());
                ps.setDouble(idx++, r.uvindex());
                ps.setDouble(idx++, r.severerisk());
                ps.setTimestamp(idx++, Timestamp.valueOf(r.sunrise()));
                ps.setTimestamp(idx++, Timestamp.valueOf(r.sunset()));
                ps.setDouble(idx++, r.moonphase());
                ps.setString(idx++, r.conditions());
                ps.setString(idx++, r.description());
                ps.setString(idx++, r.icon());

                if (r.stations().isPresent()) {
                    ps.setString(idx++, r.stations().get());
                } else {
                    ps.setNull(idx++, Types.VARCHAR);
                }

                ps.addBatch();
            }

            ps.executeBatch();
            conn.commit();
        }
    }
}

package br.edu.utfpr.etl;

import java.util.List;

public class Main {

    private static String env(String key, String defaultValue) {
        String value = System.getenv(key);
        return (value != null && !value.isEmpty()) ? value : defaultValue;
    }

    public static void main(String[] args) {
        try {
            String dbHost = env("DB_HOST", "localhost");
            String dbPort = env("DB_PORT", "5432");
            String dbName = env("DB_NAME", "meteorological");
            String dbUser = env("DB_USER", "meteo");
            String dbPassword = env("DB_PASSWORD", "meteo123");
            String csvPath = env("CSV_PATH", "../test.csv");
            String jdbcUrl = "jdbc:postgresql://" + dbHost + ":" + dbPort + "/" + dbName;

            System.out.println("=== Java Meteorological ETL ===");

            long startTime = System.nanoTime();

            // Extract
            CsvExtractor extractor = new CsvExtractor(csvPath);
            List<WeatherRecord> rawRecords = extractor.extract();

            // Transform
            Transformer transformer = new Transformer();
            List<WeatherRecord> transformedRecords = transformer.transform(rawRecords);

            // Load
            DatabaseLoader loader = new DatabaseLoader(jdbcUrl, dbUser, dbPassword);
            loader.load(transformedRecords);

            long elapsedMs = (System.nanoTime() - startTime) / 1_000_000;
            System.out.println("ETL completed in " + elapsedMs + " ms");
            System.out.println("=== ETL Complete ===");

        } catch (Exception e) {
            System.err.println("ETL failed: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}

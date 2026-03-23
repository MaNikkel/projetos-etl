package br.edu.utfpr.etl;

import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvException;

import java.io.FileReader;
import java.io.IOException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class CsvExtractor {

    private final String filePath;

    public CsvExtractor(String filePath) {
        this.filePath = filePath;
    }

    public List<WeatherRecord> extract() throws IOException, CsvException {
        List<WeatherRecord> records = new ArrayList<>();

        try (CSVReader reader = new CSVReader(new FileReader(filePath))) {
            List<String[]> rows = reader.readAll();

            // Skip header row
            for (int i = 1; i < rows.size(); i++) {
                String[] cols = rows.get(i);
                records.add(parseRow(cols));
            }
        }

        return records;
    }

    private WeatherRecord parseRow(String[] cols) {
        return new WeatherRecord(
            cols[0],                                        // name
            LocalDate.parse(cols[1]),                       // datetime
            Double.parseDouble(cols[2]),                    // tempmax
            Double.parseDouble(cols[3]),                    // tempmin
            Double.parseDouble(cols[4]),                    // temp
            Double.parseDouble(cols[5]),                    // feelslikemax
            Double.parseDouble(cols[6]),                    // feelslikemin
            Double.parseDouble(cols[7]),                    // feelslike
            Double.parseDouble(cols[8]),                    // dew
            Double.parseDouble(cols[9]),                    // humidity
            Double.parseDouble(cols[10]),                   // precip
            Double.parseDouble(cols[11]),                   // precipprob
            Double.parseDouble(cols[12]),                   // precipcover
            parseOptionalString(cols[13]),                  // preciptype
            parseOptionalDouble(cols[14]),                  // snow
            parseOptionalDouble(cols[15]),                  // snowdepth
            Double.parseDouble(cols[16]),                   // windgust
            Double.parseDouble(cols[17]),                   // windspeed
            Double.parseDouble(cols[18]),                   // winddir
            Double.parseDouble(cols[19]),                   // sealevelpressure
            Double.parseDouble(cols[20]),                   // cloudcover
            Double.parseDouble(cols[21]),                   // visibility
            Double.parseDouble(cols[22]),                   // solarradiation
            Double.parseDouble(cols[23]),                   // solarenergy
            Double.parseDouble(cols[24]),                   // uvindex
            Double.parseDouble(cols[25]),                   // severerisk
            LocalDateTime.parse(cols[26]),                  // sunrise
            LocalDateTime.parse(cols[27]),                  // sunset
            Double.parseDouble(cols[28]),                   // moonphase
            cols[29],                                       // conditions
            cols[30],                                       // description
            cols[31],                                       // icon
            parseOptionalString(cols[32])                   // stations
        );
    }

    private Optional<String> parseOptionalString(String value) {
        if (value == null || value.trim().isEmpty()) {
            return Optional.empty();
        }
        return Optional.of(value.trim());
    }

    private Optional<Double> parseOptionalDouble(String value) {
        if (value == null || value.trim().isEmpty()) {
            return Optional.empty();
        }
        return Optional.of(Double.parseDouble(value.trim()));
    }
}

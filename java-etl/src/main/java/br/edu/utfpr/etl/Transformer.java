package br.edu.utfpr.etl;

import java.util.List;

import static br.edu.utfpr.etl.UnitConverter.*;

public class Transformer {

    public List<WeatherRecord> transform(List<WeatherRecord> records) {
        return records.stream()
            .map(this::transformRecord)
            .toList();
    }

    private WeatherRecord transformRecord(WeatherRecord r) {
        return new WeatherRecord(
            r.name(),
            r.datetime(),
            fahrenheitToCelsius(r.tempmax()),
            fahrenheitToCelsius(r.tempmin()),
            fahrenheitToCelsius(r.temp()),
            fahrenheitToCelsius(r.feelslikemax()),
            fahrenheitToCelsius(r.feelslikemin()),
            fahrenheitToCelsius(r.feelslike()),
            fahrenheitToCelsius(r.dew()),
            r.humidity(),
            inchesToMm(r.precip()),
            r.precipprob(),
            r.precipcover(),
            r.preciptype(),
            r.snow().map(UnitConverter::inchesToMm),
            r.snowdepth().map(UnitConverter::inchesToMm),
            milesToKm(r.windgust()),
            milesToKm(r.windspeed()),
            r.winddir(),
            r.sealevelpressure(),
            r.cloudcover(),
            milesToKm(r.visibility()),
            r.solarradiation(),
            r.solarenergy(),
            r.uvindex(),
            r.severerisk(),
            r.sunrise(),
            r.sunset(),
            r.moonphase(),
            r.conditions(),
            r.description(),
            r.icon(),
            r.stations()
        );
    }
}

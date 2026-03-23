package br.edu.utfpr.etl;

public final class UnitConverter {

    private UnitConverter() {}

    public static double fahrenheitToCelsius(double f) {
        return round2((f - 32.0) * 5.0 / 9.0);
    }

    public static double inchesToMm(double inches) {
        return round2(inches * 25.4);
    }

    public static double milesToKm(double miles) {
        return round2(miles * 1.60934);
    }

    public static double round2(double value) {
        return Math.round(value * 100.0) / 100.0;
    }
}

module Transformer (transformRecords) where

import WeatherRecord (WeatherRecord(..))
import UnitConverter (fahrenheitToCelsius, inchesToMm, milesToKm)

transformRecords :: [WeatherRecord] -> [WeatherRecord]
transformRecords = map transformRecord

transformRecord :: WeatherRecord -> WeatherRecord
transformRecord r = r
    { wrTempmax      = fahrenheitToCelsius (wrTempmax r)
    , wrTempmin      = fahrenheitToCelsius (wrTempmin r)
    , wrTemp         = fahrenheitToCelsius (wrTemp r)
    , wrFeelslikemax = fahrenheitToCelsius (wrFeelslikemax r)
    , wrFeelslikemin = fahrenheitToCelsius (wrFeelslikemin r)
    , wrFeelslike    = fahrenheitToCelsius (wrFeelslike r)
    , wrDew          = fahrenheitToCelsius (wrDew r)
    , wrPrecip       = inchesToMm (wrPrecip r)
    , wrSnow         = fmap inchesToMm (wrSnow r)
    , wrSnowdepth    = fmap inchesToMm (wrSnowdepth r)
    , wrWindgust     = milesToKm (wrWindgust r)
    , wrWindspeed    = milesToKm (wrWindspeed r)
    , wrVisibility   = milesToKm (wrVisibility r)
    }

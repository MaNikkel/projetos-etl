{-# LANGUAGE DeriveGeneric #-}

module WeatherRecord where

import Data.Text (Text)
import Data.Time (Day, LocalTime)
import GHC.Generics (Generic)

data WeatherRecord = WeatherRecord
    { wrName            :: !Text
    , wrDatetime        :: !Day
    , wrTempmax         :: !Double
    , wrTempmin         :: !Double
    , wrTemp            :: !Double
    , wrFeelslikemax    :: !Double
    , wrFeelslikemin    :: !Double
    , wrFeelslike       :: !Double
    , wrDew             :: !Double
    , wrHumidity        :: !Double
    , wrPrecip          :: !Double
    , wrPrecipprob      :: !Double
    , wrPrecipcover     :: !Double
    , wrPreciptype      :: !(Maybe Text)
    , wrSnow            :: !(Maybe Double)
    , wrSnowdepth       :: !(Maybe Double)
    , wrWindgust        :: !Double
    , wrWindspeed       :: !Double
    , wrWinddir         :: !Double
    , wrSealevelpressure :: !Double
    , wrCloudcover      :: !Double
    , wrVisibility      :: !Double
    , wrSolarradiation  :: !Double
    , wrSolarenergy     :: !Double
    , wrUvindex         :: !Double
    , wrSevererisk      :: !Double
    , wrSunrise         :: !LocalTime
    , wrSunset          :: !LocalTime
    , wrMoonphase       :: !Double
    , wrConditions      :: !Text
    , wrDescription     :: !Text
    , wrIcon            :: !Text
    , wrStations        :: !(Maybe Text)
    } deriving (Show, Generic)

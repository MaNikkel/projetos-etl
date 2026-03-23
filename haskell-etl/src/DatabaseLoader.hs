{-# LANGUAGE OverloadedStrings #-}

module DatabaseLoader (loadRecords) where

import           WeatherRecord (WeatherRecord(..))
import           Database.PostgreSQL.Simple
import           Database.PostgreSQL.Simple.ToField (ToField, toField, Action(..))
import           Database.PostgreSQL.Simple.ToRow   (ToRow(..))
import           Database.PostgreSQL.Simple.Types   (Null(..))
import qualified Data.ByteString.Char8 as BS

instance ToRow WeatherRecord where
    toRow r =
        [ toField (wrName r)
        , toField (wrDatetime r)
        , toField (wrTempmax r)
        , toField (wrTempmin r)
        , toField (wrTemp r)
        , toField (wrFeelslikemax r)
        , toField (wrFeelslikemin r)
        , toField (wrFeelslike r)
        , toField (wrDew r)
        , toField (wrHumidity r)
        , toField (wrPrecip r)
        , toField (wrPrecipprob r)
        , toField (wrPrecipcover r)
        , maybeField (wrPreciptype r)
        , maybeField (wrSnow r)
        , maybeField (wrSnowdepth r)
        , toField (wrWindgust r)
        , toField (wrWindspeed r)
        , toField (wrWinddir r)
        , toField (wrSealevelpressure r)
        , toField (wrCloudcover r)
        , toField (wrVisibility r)
        , toField (wrSolarradiation r)
        , toField (wrSolarenergy r)
        , toField (wrUvindex r)
        , toField (wrSevererisk r)
        , toField (wrSunrise r)
        , toField (wrSunset r)
        , toField (wrMoonphase r)
        , toField (wrConditions r)
        , toField (wrDescription r)
        , toField (wrIcon r)
        , maybeField (wrStations r)
        ]

maybeField :: ToField a => Maybe a -> Action
maybeField Nothing  = toField Null
maybeField (Just v) = toField v

insertSQL :: Query
insertSQL = "INSERT INTO meteorological_data (\
    \name, datetime, tempmax, tempmin, temp, \
    \feelslikemax, feelslikemin, feelslike, dew, \
    \humidity, precip, precipprob, precipcover, preciptype, \
    \snow, snowdepth, windgust, windspeed, winddir, \
    \sealevelpressure, cloudcover, visibility, \
    \solarradiation, solarenergy, uvindex, severerisk, \
    \sunrise, sunset, moonphase, \
    \conditions, description, icon, stations\
    \) VALUES (\
    \?, ?, ?, ?, ?, \
    \?, ?, ?, ?, \
    \?, ?, ?, ?, ?, \
    \?, ?, ?, ?, ?, \
    \?, ?, ?, \
    \?, ?, ?, ?, \
    \?, ?, ?, \
    \?, ?, ?, ?)"

loadRecords :: BS.ByteString -> [WeatherRecord] -> IO ()
loadRecords connStr records = do
    conn <- connectPostgreSQL connStr
    withTransaction conn $ do
        mapM_ (execute conn insertSQL) records
    close conn

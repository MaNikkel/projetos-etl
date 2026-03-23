{-# LANGUAGE OverloadedStrings #-}

module CsvExtractor (extractCsv) where

import           WeatherRecord (WeatherRecord(..))
import qualified Data.ByteString.Lazy as BL
import           Data.Csv (HasHeader(..))
import qualified Data.Csv as Csv
import qualified Data.Vector as V
import qualified Data.Text as T
import           Data.Time (parseTimeOrError, defaultTimeLocale)
import           Data.Time.Calendar (Day)
import           Data.Time.LocalTime (LocalTime)

extractCsv :: FilePath -> IO [WeatherRecord]
extractCsv path = do
    csvData <- BL.readFile path
    case Csv.decode HasHeader csvData of
        Left err -> error $ "CSV parse error: " ++ err
        Right rows -> return $ V.toList rows
instance Csv.FromRecord WeatherRecord where
    parseRecord v
        | V.length v == 33 = WeatherRecord
            <$> v Csv..! 0                   -- name
            <*> (parseDay <$> v Csv..! 1)    -- datetime
            <*> v Csv..! 2                   -- tempmax
            <*> v Csv..! 3                   -- tempmin
            <*> v Csv..! 4                   -- temp
            <*> v Csv..! 5                   -- feelslikemax
            <*> v Csv..! 6                   -- feelslikemin
            <*> v Csv..! 7                   -- feelslike
            <*> v Csv..! 8                   -- dew
            <*> v Csv..! 9                   -- humidity
            <*> v Csv..! 10                  -- precip
            <*> v Csv..! 11                  -- precipprob
            <*> v Csv..! 12                  -- precipcover
            <*> (optionalText <$> v Csv..! 13)   -- preciptype
            <*> (optionalDouble <$> v Csv..! 14) -- snow
            <*> (optionalDouble <$> v Csv..! 15) -- snowdepth
            <*> v Csv..! 16                  -- windgust
            <*> v Csv..! 17                  -- windspeed
            <*> v Csv..! 18                  -- winddir
            <*> v Csv..! 19                  -- sealevelpressure
            <*> v Csv..! 20                  -- cloudcover
            <*> v Csv..! 21                  -- visibility
            <*> v Csv..! 22                  -- solarradiation
            <*> v Csv..! 23                  -- solarenergy
            <*> v Csv..! 24                  -- uvindex
            <*> v Csv..! 25                  -- severerisk
            <*> (parseLocalTime <$> v Csv..! 26) -- sunrise
            <*> (parseLocalTime <$> v Csv..! 27) -- sunset
            <*> v Csv..! 28                  -- moonphase
            <*> v Csv..! 29                  -- conditions
            <*> v Csv..! 30                  -- description
            <*> v Csv..! 31                  -- icon
            <*> (optionalText <$> v Csv..! 32)   -- stations
        | otherwise = fail $ "Expected 33 fields, got " ++ show (V.length v)

parseDay :: T.Text -> Day
parseDay = parseTimeOrError True defaultTimeLocale "%Y-%m-%d" . T.unpack

parseLocalTime :: T.Text -> LocalTime
parseLocalTime = parseTimeOrError True defaultTimeLocale "%Y-%m-%dT%H:%M:%S" . T.unpack

optionalText :: T.Text -> Maybe T.Text
optionalText t
    | T.null (T.strip t) = Nothing
    | otherwise          = Just (T.strip t)

optionalDouble :: T.Text -> Maybe Double
optionalDouble t
    | T.null (T.strip t) = Nothing
    | otherwise          = Just (read (T.unpack (T.strip t)))

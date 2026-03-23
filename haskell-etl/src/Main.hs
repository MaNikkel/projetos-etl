{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE RecordWildCards   #-}

module Main where

import           WeatherRecord    ()
import           CsvExtractor     (extractCsv)
import           Transformer      (transformRecords)
import           DatabaseLoader   (loadRecords)
import           System.Exit      (exitFailure)
import           System.Environment (lookupEnv)
import           Control.Exception (catch, SomeException)
import           Data.Time.Clock (getCurrentTime, diffUTCTime)
import qualified Data.ByteString.Char8 as BS

envOrDefault :: String -> String -> IO String
envOrDefault key def = do
    val <- lookupEnv key
    return $ maybe def id val

main :: IO ()
main = do
    putStrLn "=== Haskell Meteorological ETL ==="
    run `catch` handleError
  where
    run = do
        -- Config from environment
        dbHost  <- envOrDefault "DB_HOST"     "localhost"
        dbPort  <- envOrDefault "DB_PORT"     "5432"
        dbName  <- envOrDefault "DB_NAME"     "meteorological"
        dbUser  <- envOrDefault "DB_USER"     "meteo"
        dbPass  <- envOrDefault "DB_PASSWORD" "meteo123"
        csvPath <- envOrDefault "CSV_PATH"    "../test.csv"

        let connStr = BS.pack $ "host=" ++ dbHost
                             ++ " port=" ++ dbPort
                             ++ " dbname=" ++ dbName
                             ++ " user=" ++ dbUser
                             ++ " password=" ++ dbPass

        startTime <- getCurrentTime

        -- Extract
        rawRecords <- extractCsv csvPath

        -- Transform
        let transformed = transformRecords rawRecords

        -- Load
        loadRecords connStr transformed

        endTime <- getCurrentTime
        let elapsedMs = round (diffUTCTime endTime startTime * 1000) :: Integer
        putStrLn $ "ETL completed in " ++ show elapsedMs ++ " ms"
        putStrLn "=== ETL Complete ==="

    handleError :: SomeException -> IO ()
    handleError e = do
        putStrLn $ "ETL failed: " ++ show e
        exitFailure

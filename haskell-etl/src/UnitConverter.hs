module UnitConverter
    ( fahrenheitToCelsius
    , inchesToMm
    , milesToKm
    , round2
    ) where

fahrenheitToCelsius :: Double -> Double
fahrenheitToCelsius f = round2 $ (f - 32.0) * 5.0 / 9.0

inchesToMm :: Double -> Double
inchesToMm inches = round2 $ inches * 25.4

milesToKm :: Double -> Double
milesToKm miles = round2 $ miles * 1.60934

round2 :: Double -> Double
round2 v = fromIntegral (round (v * 100.0) :: Integer) / 100.0

import Network.HTTP.Conduit
import qualified Data.ByteString.Lazy as B
import qualified Data.ByteString.Char8 as C
import Data.UnixTime
import Data.Time.Clock.POSIX
import System.IO.Unsafe
import System.Environment

type Coordinate = String
type Address = String
type Timestamp = String
type JSONString = String
type URL = String
type KeyValuePair = (String,String)

-- IMPURE
getKey = unsafePerformIO $ getEnv "GOOGLE_API_KEY"

-- IMPURE
get :: URL -> String
get url = C.unpack $ B.toStrict $ unsafePerformIO $ simpleHttp url

createURL :: String -> [KeyValuePair] -> String
createURL base parameters = base ++ (makePairs parameters)
    where 
        makePairs (x:xs) = foldl (++) (makeHead x) (map (\p -> "&" ++ (makePair p)) xs)
        makeHead x = "?" ++ (makePair x)
        makePair (key,value) = key ++ "=" ++ value

getPlacesURL :: [String] -> Coordinate -> URL
getPlacesURL ty loc = createURL base [("key", key), ("location", loc), ("rankby", "distance"), ("types", makePipes ty)]
    where key = getKey
          base = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
          makePipes (x:xs) = foldl (\x y -> x ++ "|" ++ y) x xs

getTransitURL :: Coordinate -> URL
getTransitURL loc = getPlacesURL ["subway_station", "train_station", "bus_station"] loc

getRoutingURL :: Coordinate -> Coordinate -> Timestamp -> URL
getRoutingURL org des time = createURL base [("key", key), ("origin", org), ("destination", des), ("mode", "transit"), ("departure_time", time)]
    where key = getKey
          base = "https://maps.googleapis.com/maps/api/directions/json"

getGeocodeURL :: Address -> URL
getGeocodeURL add = createURL base [("key", key), ("address", add)]
    where key = getKey
          base = "https://maps.googleapis.com/maps/api/geocode/json"

--getKey :: String -> JSONString -> KeyValuePair

findClosest loc rad ty = get $ getTransitURL loc 

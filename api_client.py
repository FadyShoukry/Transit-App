"""
A Client to consume the Google Maps API.
The client can query the API for the following:
    - Directions.
    - Nearby transit stations.
"""

__author__ = "Fady Shoukry"
__email__ = "fady-magdy@hotmail.co.uk"

import requests
import re
import os
import time

# Custom Exceptions

class HTTPError(Exception):
    """
    A generic HTTP error raised when the get request fails
    """
    def __init__(self, code, error_text):
        self.code = code
        self.error_text = error_text

    def __str__(self):
        return "HTTPError " + str(self.code) + "! Response: " + self.error_text

class JSONValidationError(Exception):
    # We'll implement this later
    pass

class GoogleAPIError(Exception):
    """
    Raised when Google API status does not return 'OK'
    """
    def __init__(self, content):
        self.content = content

    def __str__(self):
        return "Google API Error: " + self.content

# Client

class MapsAPIClient(object):
    
    API_KEY = os.environ.get('GOOGLE_API_KEY', None) 
    PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    ROUTING_API_URL = "https://maps.googleapis.com/maps/api/directions/json"
    GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"

    # Private Member Methods
    
    def _validate_result(self, resp):
        # Generic HTTP Error checking
        if resp.status_code != 200:
            raise HTTPError(code=status_code, error_text=resp.text())
        else:
            try:
                json_result = resp.json()
            except:
                raise JSONValidationError

        # Google-specific error handling
        google_status = json_result.get('status', '') 
        if google_status != 'OK':
            raise GoogleAPIError(google_status)

        return json_result

    def _get_places(self, query_params={}):
        """
        Utilize the API key to send the get request to the places API
        """
        query_params['key'] = self.API_KEY
        resp = requests.get(self.PLACES_API_URL, params=query_params)

        resp_json = self._validate_result(resp)
        
        return resp_json

    # Public API

    def get_transit_stops(self, location, radius=None):
        """
        Get all transit stations within <radius> of <location>
        Defaults to ranking places by distance if no radius is provided
        """
        query_params = {'location':location, 'types':'bus_station|subway_station|train_station'}
        if radius:
            query_params['radius'] = radius

        else:
            query_params['rankby'] = 'distance'

        return self._get_places(query_params)

    def geocode(self, address):
        """
        Address (String) -> Coordinates ((Double, Double))
        Retrieve first result from geocoding; if no results, return None
        """
        query_params = {'key': self.API_KEY,
                        'address': address}

        resp = requests.get(self.GEOCODING_API_URL, params=query_params)
        resp_json = self._validate_result(resp)

        results = resp_json['results']
        if len(results) == 0:
            return None

        first_result = results[0]
        lat = first_result['geometry']['location']['lat']
        lon = first_result['geometry']['location']['lng']

        return (lat,lon)

    def get_transit_routes(self, org, des, time=str(int(time.time()))):
        """
        (Coordinate -> Coordinate -> Time (String) -> JSON)
        Get transit routes from origin to destination
        """
        query_params = {'key': self.API_KEY,
                        'origin': ("%s,%s" % (str(org[0]), str(org[1]))),
                        'destination': ("%s,%s" % (str(des[0]), str(des[1]))),
                        'departure_time': time,
                        'mode': 'transit'}

        resp = requests.get(self.ROUTING_API_URL, params=query_params)
        resp_json = self._validate_result(resp)

        return resp_json['routes']

    def get_fastest_driving_route(self, org, des):
        """
        (Coordinate -> Coordinate -> JSON)
        Get driving routes frmo origin to destination
        """
        query_params = {'key': self.API_KEY,
                        'origin': ("%s,%s" % (str(org[0]), str(org[1]))),
                        'destination': ("%s,%s" % (str(des[0]), str(des[1]))),
                        'mode': 'driving'}

        resp = requests.get(self.ROUTING_API_URL, params=query_params)
        resp_json = self._validate_result(resp)

        return resp_json['routes'][0]

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
## EXCEPTIONS ##
class HTTPError(Exception):
    """
    A generic HTTP error raised when the get request fails
    """
    def __init__(self, code, error_text):
        self.code = code
        self.error_text = error_text

    def __str__(self):
        return "HTTPError " + str(self.code) + "! Response: " + self.error_text

################
class MapsAPIClient(object):
    
    API_KEY = os.environ.get('GOOGLE_API_KEY', None) 
    PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    ROUTING_API_URL = "https://maps.googleapis.com/maps/api/directions/json"

    def _get_places(self, query_params={}):
        """
        Utilize the API key to send the get request to the places API
        """
        query_params['key'] = self.API_KEY
        resp = requests.get(self.PLACES_API_URL, params=query_params)

        if resp.status_code != 200:
            raise HTTPError(code=status_code, error_text=resp.text())
        
        return resp

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

        
        



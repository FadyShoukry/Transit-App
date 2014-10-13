"""
Hybrid transit-driving directions based on waypoints
"""

__author__ = "Jamil Dhanani"
__email__ = "jamil.dhanani@gmail.com"

import requests
import re
import os
import sys
import time

import api_client

def format_time(seconds):
    if seconds > 3600:
        return ('%d hour %d mins' % (seconds / 3600, (seconds % 3600) / 60))
    else:
        return ('%d mins' % (seconds / 60))

def humanize_route(route):
    return map(lambda step: (step['html_instructions']),
               route['legs'][0]['steps'])

def get_waypoints(route):
    return map(lambda step: (step['end_location']['lat'],
                             step['end_location']['lng']), 
               route['legs'][0]['steps'])

def get_steps(route):
    r = route['legs'][0]['steps']
    return map(lambda step: ('%s (%s)' % (step['html_instructions'], 
                                          step['duration']['text'])),
                r)

class WaypointRouter(object):
    def __init__(self):
        self.client = api_client.MapsAPIClient()

    def calculate_alternatives_for_route(self, route, s, t):
        waypoints = get_waypoints(route)
        
        # Get alternate routes -- from waypoint to destination
        # Assuming you drive to waypoint, and transit from there 
        alt_routes = map(lambda waypoint: 
                            self.client.get_transit_routes(waypoint, t, delay=True),
                         waypoints)

        # Flatten list; create list of possible routes
        alt_routes = reduce(lambda x,y: x + y, alt_routes)

        # Filter those that actually have legs
        # We don't want to examine routes that are trivial (Point A -> Point A)
        alt_routes = filter(lambda route: route.get('legs'), alt_routes)

        return alt_routes

    # Get routes from source 's' to terminal 't'
    # s and t are addresses
    def get_routes(self, s, t):
        s_loc = self.client.geocode(s)
        t_loc = self.client.geocode(t)

        routes = self.client.get_transit_routes(s_loc, t_loc)

        alt_routes = []
        for route in routes:
            alt_routes.append(self.calculate_alternatives_for_route(route, s_loc, t_loc))

        # Flatten list to get list of alternate routes
        alt_routes = reduce(lambda x,y: x + y, alt_routes)

        for route in alt_routes:
            transit_r = route['legs'][0]

            start_loc = (transit_r['start_location']['lat'], transit_r['start_location']['lng'])
            route_d = self.client.get_fastest_driving_route(s_loc, start_loc)

            driving_r = route_d['legs'][0]

            print('--------')
            print('Drive to %s (%s)' % (transit_r['start_address'], 
                                        driving_r['duration']['text']))
            print('Transit to %s (%s)' % (transit_r['end_address'], 
                                          transit_r['duration']['text']))
            map(lambda s: sys.stdout.write('\t' + s + '\n'), get_steps(route))
            print('Total time: %s' % format_time(driving_r['duration']['value'] + 
                                                 transit_r['duration']['value']))
            print('--------')


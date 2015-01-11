import requests

from collections import defaultdict


class Here:

    api_base_url = 'http://route.cit.api.here.com/'

    def __init__(self, app_id, app_code):
        self.app_secret = {'app_id': app_id, 'app_code': app_code}

    def request(self, action, method='get', params=None):
        ''' Generic API request method for functions not yet implemented.

            Ex: here.request('routing/7.2/calculateroute', 'get', params)
        '''

        if method.lower() not in ['get', 'post']:
            raise Exception('Invalid method %s' % (method))

        requests_get_or_post = getattr(requests, method, None)
        api_url = "%s%s.json" % (self.api_base_url, action)

        if params is None:
            params = self.app_secret
        else:
            params = dict(params.items() + self.app_secret.items())

        data = requests_get_or_post(api_url, params=params)

        return data.json()

    def get_directions(self, waypoints):
        ''' Get directions for given coordinates

            Assumes that waypoints is a list of two or more lat/lon tuples.
        '''

        waypoint_params = {}
        for i in xrange(len(waypoints)):
            waypoint = 'geo!%f,%f' % (waypoints[i][0], waypoints[i][1])
            waypoint_params['waypoint%d' % i] = waypoint

        # TODO: Ask Jared about Platform Data Extension (specifically Blackspots,
        #       but also curvature and slope, railroad crossings, stops.
        params = {
            'mode': 'fastest;car;traffic:enabled',
            'legAttributes': 'baseTime,trafficTime,links',
            'linkAttributes': 'speedLimit,dynamicSpeedInfo,maneuver',
            'maneuverAttributes': 'position,travelTime,length,time,link,signPost,'
                                + 'action,direction,baseTime,trafficTime,waitTime,'
                                + 'freewayExit'}

        params = dict(params.items() + waypoint_params.items())

        data = self.request('routing/7.2/calculateroute', 'get', params)

        segment_list = []
        link_list = defaultdict(list)
        for leg in data.get('response', {}).get('route', [{}])[0].get('leg', []):
            for link in leg.get('link', []):
                try:
                    link_segment = {
                        '_id': str(link.get('maneuver')),
                        # Convert meters per second to miles per hour
                        'speed_limit': round(float(link.get('speedLimit')) * 2.237)
                    }

                    link_list[link_segment['_id']].append(link_segment)
                except TypeError:
                    pass
                    # print "WARN: speedLimit missing from link"

            for maneuver in leg.get('maneuver', []):
                segment = {
                    'direction': str(maneuver.get('direction')),
                    'action': str(maneuver.get('action')),
                    'speed_limit': [],
                    'traffic_time': int(maneuver.get('trafficTime')),
                    'base_time': int(maneuver.get('baseTime')),
                    'freeway_exit': str(maneuver.get('freewayExit')),
                    '_id': str(maneuver.get('id'))}

                # Add the speed from list of links
                all_speeds = set([l['speed_limit'] for l in link_list.get(segment['_id'], [])])
                segment['speed_limit'] = list(all_speeds)

                # Don't add 'arrive' actions
                if segment['action'] != 'arrive':
                    segment_list.append(segment)

        return segment_list

    def get_directions_bmw_data(self):
        ''' Routing data specific to the BMW sample route. Used as a training set for our
            machine learning algorithm. '''

        return self.get_directions([
            [37.788297, -122.401527],
            [37.786214, -122.398987],
            [37.783356, -122.402695],
            [37.593055, -122.366036]])

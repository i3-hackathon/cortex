from collections import defaultdict
from here import Here


def get_directions(here):
    ''' This method gets directions for the BMW sample route, and normalizes
        the output so we can feed it into our machine learning algorithm. '''

    params = {
        'waypoint0': 'geo!37.788297,-122.401527',
        'waypoint1': 'geo!37.786214,-122.398987',
        'waypoint2': 'geo!37.783356,-122.402695',
        'waypoint3': 'geo!37.593055,-122.366036',
        'mode': 'fastest;car;traffic:enabled',
        'legAttributes': 'baseTime,trafficTime,links',
        'linkAttributes': 'speedLimit,dynamicSpeedInfo,maneuver',
        'maneuverAttributes': 'position,travelTime,length,time,link,signPost,'
                            + 'action,direction,baseTime,trafficTime,waitTime'}
    data = here.request('routing/7.2/calculateroute', 'get', params)

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
                print "WARN: speedLimit missing from link"

        for maneuver in leg.get('maneuver', []):
            segment = {
                'direction': str(maneuver.get('direction')),
                'action': str(maneuver.get('action')),
                'speed_limit': [],
                'traffic_time': int(maneuver.get('trafficTime')),
                'base_time': int(maneuver.get('baseTime')),
                '_id': str(maneuver.get('id'))}

            # Add the speed from list of links
            all_speeds = set([l['speed_limit'] for l in link_list.get(segment['_id'], [])])
            segment['speed_limit'] = list(all_speeds)

            # Don't add 'arrive' actions
            if segment['action'] != 'arrive':
                segment_list.append(segment)

    return segment_list

if __name__ == '__main__':
    here = Here(app_id='6QnZmVcfu8HXl5O4D11u',
                app_code='4KTi0jcgtuuMXlCT2SvPUQ')

    for segment in get_directions(here):
        print segment

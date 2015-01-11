import math
import requests


class BMW:

    api_base_url = 'http://data.api.hackthedrive.com/v1/'
    oauth_url = 'https://data.api.hackthedrive.com/OAuth2/authorize'

    def __init__(self, app_id, app_secret, access_token=None, redirect_uri=None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.redirect_uri = redirect_uri

    def request(self, action, method='get', params=None):
        ''' Generic API request method for functions not yet implemented '''

        # Ensure the request is either get or post
        if method.lower() not in ['get', 'post']:
            raise Exception('Invalid method %s' % (method))

        # Add appropriate headers for user authentication
        headers = {'MojioAPIToken': self.access_token}

        # Create the request function and URL
        requests_get_or_post = getattr(requests, method, None)
        api_url = "%s%s/" % (self.api_base_url, action)

        # Make the request
        data = requests_get_or_post(api_url, headers=headers, params=params)

        # Return the data
        return data.json()

    def oauth_authorize_url(self):
        ''' Returns the OAuth authorize URL so we can get an access token. '''

        params = {
            'response_type': 'token',
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
        }

        authorize = requests.get(self.oauth_url, params=params, verify=False)

        return authorize.url

    def get_environment(self):
        ''' Returns the current driving environment based on sensor data '''

        # Retrieve the most recent couple of events
        request = self.request('Events', 'get', params={'limit': 3})
        statuses = request.get('Data', [])

        if len(statuses) is 0:
            raise Exception('No Vehicle Events.')

        status = statuses[0]

        # Unique events that have occured in the last few seconds
        recent_events = list(set([str(s['EventType']) for s in statuses]))

        environment = {
            'accelerometer_threshold': 'Accelerometer' in recent_events,
            'heading_change': 'HeadingChange' in recent_events,
            'lane_departure': 'LaneDeparture' in recent_events,
            'rpm_threshold': 'RPM' in recent_events,
            'speed_threshold': 'Speed' in recent_events,
            'turn_signal': 'TurnSignal' in recent_events,
            'accelerometer': 0,
            'speed': float(status.get('Speed', 0)),
            'accelerator_pedal': float(status.get('AcceleratorPedal', 0)),
            'brake_torque': float(status.get('BrakeTorque', 0)),
            'cruise_control': status.get('CruiseControlEnabled') is not None,
            'rain_intensity': float(status.get('RainIntensity', 0)),
            'steering_wheel_angle': float(status.get('SteeringWheelAngle', 0)),
        }

        # Calculate accelerometer
        accel_x = status.get('Accelerometer', {}).get('X', 0)
        accel_y = status.get('Accelerometer', {}).get('Y', 0)
        accel_z = status.get('Accelerometer', {}).get('Z', 0)

        environment['accelerometer'] = math.sqrt((accel_x ** 2) + (accel_y ** 2) + (accel_z ** 2))

        return environment

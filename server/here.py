import requests


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

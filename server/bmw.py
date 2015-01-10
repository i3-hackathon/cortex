import requests


class BMW:

    api_base_url = 'http://api.hackthedrive.com'

    def __init__(self):
        # No API key necessary!
        pass

    def request(self, action, method, params=None):
        ''' Generic API request method for functions not yet implemented.

            Ex: vehicles = bmw.requests('vehicle', 'get')
        '''

        if method.lower() not in ['get', 'post']:
            raise Exception('Invalid method %s' % (method))

        requests_get_or_post = getattr(requests, method, None)
        api_url = "%s/%s/" % (self.api_base_url, action)

        data = requests_get_or_post(api_url, params=params)

        return data.json()

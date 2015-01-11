import os

from ai import hcl_compute
from ai import processed_route_10sinterval as demo_data
from bmw import BMW
from cors import crossdomain
from flask import Flask, jsonify, redirect
from here import Here


debug_mode = True
app_name = 'Shift'

app = Flask(__name__, static_folder='../static', static_url_path='')

domain = 'http://crispybacon.ngrok.com'
here = Here(app_id='6QnZmVcfu8HXl5O4D11u', app_code='4KTi0jcgtuuMXlCT2SvPUQ')
bmw = BMW(app_id='2d8a7423-5ea7-4053-a704-0d69dc4e13a9',
          app_secret='e0c2dc59-281a-4075-ad96-47d145479dc6',
          access_token='edd44c7f-b6c1-4c8c-80de-00aa1644071d',
          redirect_uri='%s/authorize' % (domain))


@app.route('/')
@crossdomain(origin='*')
def home():
    return ''


@app.route('/oauth-token')
@crossdomain(origin='*')
def oauth_token():
    return redirect(bmw.oauth_authorize_url())


@app.route('/authorize', defaults={'access_token': None})
@app.route('/authorize/<access_token>')
@crossdomain(origin='*')
def oauth2_authorize(access_token):
    if access_token is None:
        return '''
        <script type="text/javascript">
            // Retrieve the token from the URL
            token = window.location.href.split("access_token=")[1];
            token = token.split("&")[0];

            // Redirect to set the token
            window.location = "/authorize/" + token
        </script>
        '''
    else:
        bmw.access_token = access_token
        return redirect('/')


# Demo
demo_data_point = 0
demo_trigger_state = 0
demo_states_remaining = 1


@app.route('/environment')
@crossdomain(origin='*')
def get_environment():
    ''' This endpoint will get pinged by the mobile app every second in order
        to figure out the driving status. In a non-hackathon environment this
        would be asynchronous with websockets. '''

    # Real
    #
    # environment = bmw.get_environment()
    # return jsonify({'results': bmw.get_environment()})

    # Demo
    global demo_data_point, demo_trigger_state, demo_states_remaining

    demo_data_slice = demo_data.data[demo_data_point]

    trigger, context, states_remaining = hcl_compute.transform_delta_to_event(demo_data_point,
                                                demo_data_slice, demo_trigger_state, demo_states_remaining)

    demo_data_point = (demo_data_point + 1) % len(demo_data.data)
    demo_trigger_state = trigger
    demo_states_remaining = states_remaining

    return jsonify({'result': demo_data_slice, 'context': context})


@app.route('/directions/<coordinates>')
@crossdomain(origin='*')
def get_directions(coordinates):
    ''' Get driving directions for a series of coordinates. Coordinates should
        be passed in comme and semicolon separated.
        Ex: 37.788297,-122.401527;37.786214,-122.398987;37.783356,-122.402695
    '''

    all_coordinates = []

    # Fixes a jQuery CORS issue
    coordinates = coordinates.split('&')[0]

    # Parse the coordinates
    for coordinate_pair in coordinates.split(';'):
        all_coordinates.append(map(float, coordinate_pair.split(',')))

    directions = here.get_directions(all_coordinates)

    # "timestamps" are the markers between safe and unsafe zones
    # "unsafe" is the safety of every zone (0 1 0 1 ...)
    # "hcl_vector" shows the hcl score for every point in time
    # "parse_interval" number of seconds in each point of the hcl_vector
    timestamps, unsafe, hcl_vector, parse_interval = hcl_compute.compute_hcl(directions)

    # Demo
    global demo_trigger_state, demo_states_remaining, demo_data_point
    demo_data_point = 0
    demo_trigger_state = unsafe[0]
    demo_states_remaining = 0

    return jsonify({'result': directions})


@app.route('/bmw')
@crossdomain(origin='*')
def get_bmw_data():
    ''' Demo route. '''

    directions = here.get_directions_bmw_data()
    timestamps, unsafe, hcl_vector, parse_interval = hcl_compute.compute_hcl(directions)

    # Demo
    global demo_trigger_state, demo_states_remaining, demo_data_point
    demo_data_point = 0
    demo_trigger_state = 0
    demo_states_remaining = 0

    return jsonify({'result': directions})


if __name__ == '__main__':
    host = str(os.getenv('HOST', '0.0.0.0'))
    port = int(os.getenv('PORT', 8080))

    app.run(host=host, port=port, debug=debug_mode)

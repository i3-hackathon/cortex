import os

from flask import Flask, jsonify
from here import Here

debug_mode = True
app_name = 'Shift'

app = Flask(__name__, static_folder='../static', static_url_path='')
here = Here(app_id='6QnZmVcfu8HXl5O4D11u', app_code='4KTi0jcgtuuMXlCT2SvPUQ')


@app.route('/')
def home():
    return ''


@app.route('/directions/<coordinates>')
def get_directions(coordinates):
    ''' Get driving directions for a series of coordinates. Coordinates should
        be passed in comme and semicolon separated.
        Ex: 37.788297,-122.401527;37.786214,-122.398987;37.783356,-122.402695
    '''

    all_coordinates = []
    for coordinate_pair in coordinates.split(';'):
        all_coordinates.append(map(float, coordinate_pair.split(',')))

    return jsonify({'result': here.get_directions(all_coordinates)})


@app.route('/bmw')
def get_bmw_data():
    return jsonify({'result': here.get_directions_bmw_data()})

if __name__ == '__main__':
    host = str(os.getenv('HOST', '0.0.0.0'))
    port = int(os.getenv('PORT', 8080))

    app.run(host=host, port=port, debug=debug_mode)

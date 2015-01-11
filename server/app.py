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


@app.route('/bmw')
def get_bmw_data():
    return jsonify({'result': here.get_directions_bmw_data()})

if __name__ == '__main__':
    host = str(os.getenv('HOST', '0.0.0.0'))
    port = int(os.getenv('PORT', 8080))

    app.run(host=host, port=port, debug=debug_mode)

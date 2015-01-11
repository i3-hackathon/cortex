Shift
=====

Distractions while driving are a leading cause of vehicle accidents on the road. Using the sensor readings from the BMW Car Data API as well as current road conditions using the Here API, we calculate moments of high cognitive load (HCL) in real time in order to detect potentially dangerous situations that require the driver's full attention. The result is more than just a score, but a platform that can be used by other applications to change their user engagement based on the context of driving conditions. Built for BMW Hack the Drive.

## Setup
1. Run `./setup.sh`
2. Open `app.py` and edit the domain to your host
3. Run `python server/app.py`
4. Go to `/oauth-token` to generate an OAuth token

Note: When using Vagrant, to log into the box run `vagrant ssh -- -X`

## Front End Setup
1. Install `nodejs` and `npm`
2. Run `npm install` within the `app/` directory
3. Useful commands are: `gulp clean`, `gulp assets`
4. To run the app server, run `http-server`

## APIs Used
1. BMW Car Data (http://data.hackthedrive.com/)
2. Here (http://developer.here.com)

### Errors

`TclError: couldn't connect to display "localhost:10.0"`
Quit the Vagrant shell and log back in using `vagrant ssh -- -X`
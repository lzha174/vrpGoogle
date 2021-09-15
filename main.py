
from createRoute import GoogleMap
import requests
from flask import Flask, render_template
import vrp
import data
app = Flask(__name__)
app.config['API_KEY'] = data.apik

def extract_lat_long_via_address(address_or_zipcode):
    lat, lng = None, None
    api_key = app.config['API_KEY']
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    endpoint = f"{base_url}?address={address_or_zipcode}&key={api_key}"
    # see how our endpoint includes our API key? Yes this is yet another reason to restrict the key
    r = requests.get(endpoint)
    if r.status_code not in range(200, 299):
        return None, None
    try:
        '''
        This try block incase any of our inputs are invalid. This is done instead
        of actually writing out handlers for all kinds of responses.
        '''
        results = r.json()['results'][0]
        lat = results['geometry']['location']['lat']
        lng = results['geometry']['location']['lng']
    except:
        pass
    return lat, lng


@app.route('/')
def index():

    routenames = vrp.solvevrp()
    routePoints = data.getStaticPoints()
    #routePoints = getAPILocations(routenames)
    googleMap = GoogleMap(routePoints, routenames)
    context = {
        "key": app.config['API_KEY'],
        "title": 'VRT',
        "addresses": data.addresses,
        "routeNames":googleMap.getNames
    }
    routes= googleMap.getRoute()
    return render_template('template.html', mymap=googleMap, context=context, routes = routes)


def getAPILocations(routenames):
    routePoints= []
    for names in routenames:
        points = []
        for name in names:
            lat,lng = extract_lat_long_via_address(name)
            point = (lat,lng)
            points.append(point)
        routePoints.append(points)
    return  routePoints
import os
if __name__=="__main__":

    app.run(host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', 4444)))

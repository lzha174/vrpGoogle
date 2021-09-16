
from createRoute import GoogleMap
import requests
from flask import Flask, render_template
import vrp
import data
import os
from queue import Queue
from threading import Thread

app = Flask(__name__)
app.config['API_KEY'] = data.apik

routenames = None
routePoints = None
googleMap = None

def solveVRP(q):
    routenames = vrp.solvevrp()
    #routePoints = data.getStaticPoints()
    routePoints = getAPILocations(routenames)
    googleMap = GoogleMap(routePoints, routenames)
    q.put((routenames, routePoints, googleMap))


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
    global googleMap
    while q.empty() == False:
        values = q.get()
        routenames = values[0]
        routePoints = values[1]
        googleMap = values[2]


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

if __name__=="__main__":
    q = Queue()
    thread1 = Thread(target=solveVRP, args=(q,), daemon=True)
    thread1.start()
    app.run(host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', 4444)))

import math


class GoogleMap:
    def __init__(self, points, routenames):
        """
        Instantiate an Map object with route corodinates added to the Map object
        :param points: a list of a list of tuples contains latitude and longitude of a route
        """
        self._points = points
        self.routeNames = routenames
        self.google_coordinates = []
        for route in points:
            coords = ",\n".join(["{{lat: {lat}, lng: {lng}}}".format(lat=x, lng=y) for x, y, *rest in route])
            self.google_coordinates.append(coords)
        print(self.google_coordinates)

    @property
    def zoom(self):
        """
        Algorithm to derive zoom from a route. For details please see
        - https://developers.google.com/maps/documentation/javascript/maptypes#WorldCoordinates
        - http://stackoverflow.com/questions/6048975/google-maps-v3-how-to-calculate-the-zoom-level-for-a-given-bounds
        :return: zoom value 0 - 21 based on the how widely spread of the route coordinates
        """

        map_size = {"height": 1200, "width": 1900}
        max_zoom = 21   # maximum zoom level based on Google Map API
        world_dimension = {'height': 500, 'width': 256}     # min map size for entire world

        latitudes = [lat for lat, lon, *rest in self._points[0]]
        longitudes = [lon for lat, lon, *rest in self._points[0]]

        # calculate longitude span between east and west
        delta = max(longitudes) - min(longitudes)
        if delta < 0:
            lon_span = (delta + 360) / 360
        else:
            lon_span = delta / 360

        # calculate latitude span between south and north
        lat_span = (self._lat_rad(max(latitudes)) - self._lat_rad(min(latitudes))) / math.pi

        # get zoom for both latitude and longitude
        zoom_lat = math.floor(math.log(map_size['height'] / world_dimension['height'] / lat_span) / math.log(2))
        zoom_lon = math.floor(math.log(map_size['width'] / world_dimension['width'] / lon_span) / math.log(2))
        return 11

    @property
    def center(self):
        """
        Calculate the center of the current map object
        :return: (center_lat, center_lng) latitude, longitude represents the center of the map object
        """
        center_lat = (max((x[0] for x in self._points[0])) + min((x[0] for x in self._points[0]))) / 2
        center_lng = (max((x[1] for x in self._points[0])) + min((x[1] for x in self._points[0]))) / 2
        return center_lat, center_lng


    @staticmethod
    def _lat_rad(lat):
        """
        Helper function for calculating latitude span
        """
        sinus = math.sin(math.radians(lat + math.pi / 180))
        rad_2 = math.log((1 + sinus) / (1 - sinus)) / 2
        return max(min(rad_2, math.pi), -math.pi) / 2

    def getRoute(self):
        return  self.google_coordinates

    @property
    def getNames(self):
        routeNames = []
        for names in self.routeNames:
            p = ' --> '.join(names)
            routeNames.append(p)
        return routeNames
from flask.ext.restful import Resource
from flask_restful import reqparse
from database_settings import CrimeModel, session
from geoalchemy2 import Geometry, WKTElement
from geoalchemy2.functions import ST_AsGeoJSON
from collections import defaultdict
from sqlalchemy import func
from geojson import Point, Polygon, LineString, Feature, FeatureCollection
import geojson
from utils.resource_utils import base_response

def polygonQuery(coordinates):
    poly = WKTElement("POLYGON((" + coordinates + "))", srid=4236)
    crimes = session.query(CrimeModel.category, ST_AsGeoJSON(CrimeModel.geom)).filter(CrimeModel.geom.ST_Intersects(poly))
    return crimes

def parseCoordinates(coord_string):
    temp = coord_string.split(",")
    temp2 = [x.split(" ") for x in temp]
    return [(float(x),float(y)) for x, y in temp2]

def featurize(point):
    geom = geojson.loads(point[1])
    props = {"crime_category":point[0]}
    feature = Feature(geometry=geom, properties=props)
    return feature

class Crime(Resource):
    """
    Crime Polygon Class that wraps
    polygon types for the crime table
    """
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=str, required=True)
        parser.add_argument("coordinates", type=str, required=True)
        args = parser.parse_args()
        resp = base_response()
        poly = Polygon(parseCoordinates(args.coordinates))

        if args.type.lower() == "polygon":
            crimes = FeatureCollection([featurize(x) for x in polygonQuery(args.coordinates)])

        print crimes



        return {"end":"true"}, 200
        try:
            poly_query = WKTElement(
                'POLYGON((' + coordinates + '))', srid=4326)
            crime_cat = session.query(CrimeModel.category, func.count(CrimeModel.category)) \
                .filter(CrimeModel.geom.ST_Intersects(poly_query)) \
                .group_by(CrimeModel.category)

            crime_dict = defaultdict(list)
            for crime in crime_cat:
                crime_dict[crime[0]] = crime[1]
            c1 = coordinates.split(",")
            c2 = [x.split(" ") for x in c1]
            coords = [[float(l1), float(l2)] for l1, l2 in c2]
            return {"data": crime_dict, "coordinates": coords}, 200
        except:
            session.rollback()
            return {}, 400

from flask.ext.restful import Resource
from flask_restful import reqparse
from database_settings import CrimeModel, session
from geoalchemy2 import Geometry, WKTElement
from geoalchemy2.functions import ST_AsGeoJSON
from sqlalchemy import func
from geojson import Point, Polygon, LineString, Feature, FeatureCollection
import datetime
import geojson
# https://github.com/frewsxcv/python-geojson
from utils.resource_utils import base_response


def polygonQuery(coordinates):
    poly = WKTElement("POLYGON((" + coordinates + "))", srid=4236)
    crimes = session.query(
        CrimeModel.category, CrimeModel.descript, CrimeModel.date,
        CrimeModel.time, CrimeModel.resolution, CrimeModel.pddistrict,
        CrimeModel.dayofweek, ST_AsGeoJSON(CrimeModel.geom)).filter(
            CrimeModel.geom.ST_Intersects(poly)).limit(200)
    return crimes


def parseCoordinates(coord_string):
    temp = coord_string.split(",")
    temp2 = [x.split(" ") for x in temp]
    return [(float(x), float(y)) for x, y in temp2]


def featurize(point):
    geom = geojson.loads(point[7])
    features = ["category", "description", "date", "time", "resolution",
                "pddistrict", "dayofweek"]
    props = {}
    for count, val in enumerate(features):
        props[val] = point[count]

    if "date" in props:
        props['date'] = props['date'].strftime('%Y-%m-%d')

    if "time" in props:
        props['time'] = props['time'].strftime('%H:%M:%S')

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
        parser.add_argument("start_date", type=str)
        parser.add_argument("end_date", type=str)
        args = parser.parse_args()
        resp = base_response()
        poly = Polygon(parseCoordinates(args.coordinates))

        try:
            if args.type.lower() == "polygon":
                crimes = FeatureCollection([
                    featurize(x) for x in polygonQuery(args.coordinates)
                ])
            resp['geojson_crime'] = crimes
            resp['message'] = None
            resp['geojson_shape'] = poly
            return resp, 200
        except ValueError:
            session.rollback()
            return {}, 400

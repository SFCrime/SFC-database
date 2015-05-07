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

# need to add in filter support for dates, this means that we need to
# change the parms for this function as well as the filter which can be
# comma seperated


def polygonQuery(coordinates, start_date, end_date):
    poly = WKTElement("POLYGON((" + coordinates + "))", srid=4236)
    crimes = session.query(
        CrimeModel.category, CrimeModel.descript, CrimeModel.date,
        CrimeModel.time, CrimeModel.resolution, CrimeModel.pddistrict,
        CrimeModel.dayofweek, ST_AsGeoJSON(CrimeModel.geom)).filter(
            CrimeModel.geom.ST_Intersects(poly), CrimeModel.date > start_date,
            CrimeModel.date < end_date)
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


def EvEComparison(args):
    crimes_1 = FeatureCollection([featurize(x) for x in polygonQuery(
        args.coordinates, args.start_date_1, args.end_date_1)])
    crimes_2 = FeatureCollection([featurize(x) for x in polygonQuery(
        args.coordinates, args.start_date_2, args.end_date_2)])
    return [crimes_1, crimes_2]


def EvBaselineComparison(args):
    crimes_1 = FeatureCollection([featurize(x) for x in polygonQuery(
        args.coordinates, args.start_date_1, args.end_date_1)])
    # here's where we need to include the baseline calculations
    crimes_2 = None
    return [crimes_1, crimes_2]


class Crime(Resource):
    """
    Crime Polygon Class that wraps
    polygon types for the crime table
    """

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=str, required=True)
        parser.add_argument('geo_type', type=str, required=True)
        parser.add_argument("coordinates", type=str, required=True)
        parser.add_argument("start_date_1", type=str, required=True)
        parser.add_argument("start_date_2", type=str, required=True)
        parser.add_argument("end_date_1", type=str)
        parser.add_argument("end_date_2", type=str)
        args = parser.parse_args()
        resp = base_response()
        poly = Polygon(parseCoordinates(args.coordinates))

        try:
            if args.type == "1v1":
                crime = EvEComparison(args)
            else:
                crime = EvBaselineComparison(args)
            resp['geojson_crime'] = crime
            resp['message'] = None
            resp['geojson_shape'] = poly
            return resp, 200
        except ValueError:
            session.rollback()
            return {}, 400

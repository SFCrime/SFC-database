from flask.ext.restful import Resource
from database_settings import CrimeModel, session
from geoalchemy2 import Geometry, WKTElement
from collections import defaultdict
from sqlalchemy import func

class Crime(Resource):

    """
    Crime Polygon Class that wraps
    polygon types for the crime table
    """

    def get(self, coordinates):
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


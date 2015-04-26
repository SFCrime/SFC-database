#!/usr/bin/env python
from flask import Flask, jsonify, make_response
from flask.ext import restful

from sqlalchemy import Column, Integer, String, Date, \
    Time, Float, create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from geoalchemy2 import Geometry, WKTElement
from collections import defaultdict
import psycopg2

app = Flask(__name__)
api = restful.Api(app)

## database
database = 'postgresql://info247:test@localhost:5432/sfpd'
engine = create_engine(database)
Session = sessionmaker(bind=engine)
session = Session()

crime_api_v1 = "/api/v1/crime/"

def response_decorator(func):
    """Provides a decorator function to
    embed our response within a response object"""
    def func_wrap(*args, **kwargs):
        return {"response": func(*args, **kwargs)}
    return func_wrap

Base = declarative_base()
class Crime(Base):
    """
    Crime Table
    """
    __tablename__ = 'crime'
    incidntnum = Column(Integer)
    category = Column(String)
    descript = Column(String)
    dayofweek = Column(String)
    date = Column(Date)
    time = Column(Time)
    pddistrict = Column(String)
    resolution = Column(String)
    address = Column(String)
    x = Column(Float)
    y = Column(Float)
    pdid = Column(Integer, primary_key=True)
    geom = Column(Geometry('geography'))



class CrimePolygon(restful.Resource):
    def get(self, coordinates):
        try:
            poly_query = WKTElement('POLYGON((' + coordinates + '))', srid=4326)
            crime_cat = session.query(Crime.category, func.count(Crime.category)) \
                .filter(Crime.geom.ST_Intersects(poly_query)) \
                .group_by(Crime.category)

            crime_dict = defaultdict(list)
            for crime in crime_cat:
                crime_dict[crime[0]] = crime[1]
            return crime_dict, 200
        except:
            return {}, 400


api.add_resource(CrimePolygon, crime_api_v1 + "polygon/<coordinates>")

if __name__ == '__main__':
    app.run(debug=True)


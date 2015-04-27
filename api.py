#!/usr/bin/env python
from flask import Flask, jsonify, make_response
from flask.ext import restful
from flask.ext.cors import CORS
from flask.ext.restful import fields, marshal_with

from sqlalchemy import Column, Integer, String, Date, \
    Time, Float, Boolean, create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from geoalchemy2 import Geometry, WKTElement
from geoalchemy2.shape import to_shape
from collections import defaultdict
import psycopg2
import re

app = Flask(__name__)
cors = CORS(app, resources=r"/api/*", allow_headers="Content-Type",
            supports_credentials=True)
api = restful.Api(app)

# database
database = 'postgresql://info247:test@localhost:5432/sfpd'
engine = create_engine(database)
Session = sessionmaker(bind=engine)
session = Session()

api_version = "/api/v1/"

crime_api = api_version + "crime/"
events_api = api_version + "events/"

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
    x = Column(Float)  # this is the longitude
    y = Column(Float)  # this is latitude
    pdid = Column(Integer, primary_key=True)
    geom = Column(Geometry('geography'))


class EventDb(Base):

    """
    Events Table
    """
    __tablename__ = "events"
    id_name = Column(String, primary_key=True)
    name = Column(String)
    year = Column(Integer)
    start_date = Column(Date)
    start_time = Column(Time)
    end_date = Column(Date)
    end_time = Column(Time)
    is_point = Column(Boolean)
    is_polygon = Column(Boolean)
    is_line = Column(Boolean)
    polygon = Column(Geometry('geography'))
    line = Column(Geometry('geography'))
    point = Column(Geometry('geography'))


class Event(restful.Resource):

    def get(self, event_id):
        try:
            res = session.query(EventDb).filter(
                EventDb.id_name == event_id).first()
            if res == None:
                raise AttributeError("No Event")

            res.start_time = str(res.start_time)
            res.end_time = str(res.end_time)
            res.end_date = str(res.end_date)
            res.start_date = str(res.start_date)
            res.shape_type = ""

            if res.is_polygon:
                res.shape_type = "polygon"
                res.shape_string = str(to_shape(res.polygon))
                temp = re.findall(r"\(\((.*)\)\)", res.shape_string)
                print temp
                t2 = temp[0].split(", ")
                t3 = [val.split(" ") for val in t2]
                res.shape_list = [[float(l1), float(l2)] for l1, l2 in t3]

            del(res.point)
            del(res.polygon)
            del(res.line)
            del(res.is_point)
            del(res.is_line)
            del(res.is_polygon)
            del(res._sa_instance_state)

            return dict(vars(res).iteritems()), 200

        except:
            session.rollback()
            return {}, 400

    def post(self, event_id):
        pass


class CrimePolygon(restful.Resource):

    """
    Crime Polygon Class that wraps
    polygon types for the crime table
    """

    def get(self, coordinates):
        try:
            poly_query = WKTElement(
                'POLYGON((' + coordinates + '))', srid=4326)
            crime_cat = session.query(Crime.category, func.count(Crime.category)) \
                .filter(Crime.geom.ST_Intersects(poly_query)) \
                .group_by(Crime.category)

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


api.add_resource(CrimePolygon, crime_api + "polygon/<coordinates>")
api.add_resource(Event, events_api + "<event_id>")

if __name__ == '__main__':
    app.run(debug=True)

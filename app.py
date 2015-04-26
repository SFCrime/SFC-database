#!/usr/bin/env python
from flask import Flask, jsonify, make_response
from sqlalchemy import Column, Integer, String, Date, \
    Time, Float, create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry, WKTElement
from collections import defaultdict


app = Flask(__name__)

## database
Base = declarative_base()

class Crime(Base):
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

database = 'postgresql://info247:test@localhost:5432/sfpd'
engine = create_engine(database)
Session = sessionmaker(bind=engine)
session = Session()


## views
@app.route('/api/v1/polygon/<coordinates>', methods=['GET'])
def index(coordinates):
    '''
    # View all crimes in Dolores Park by crime category

    $ curl -i 'http://localhost:5000/api/v1/polygon/%2D122.42841124534607%2037.76128348360843%2C%2D122.42810010910034%2037.7580942260561%2C%2D122.42584705352783%2037.75822145970878%2C%2D122.42613673210143%2037.76141071177564%2C%2D122.42841124534607%2037.76128348360843'
    '''
    poly_query = WKTElement('POLYGON((' + coordinates + '))', srid=4326)

    crime_cat = session.query(Crime.category, func.count(Crime.category)) \
        .filter(Crime.geom.ST_Intersects(poly_query)) \
        .group_by(Crime.category)

    crime_dict = defaultdict(list)
    for crime in crime_cat:
        crime_dict[crime[0]] = crime[1]

    return jsonify({'crimes': crime_dict})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)


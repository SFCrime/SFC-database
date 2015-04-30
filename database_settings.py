from sqlalchemy import Column, Integer, String, Date, \
    Time, Float, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry, WKTElement


database = 'postgresql://info247:test@localhost:5432/sfpd'
engine = create_engine(database)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class CrimeModel(Base):
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


class EventModel(Base):

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
    shape_type = Column(String)
    shape = Column(Geometry('geography'))

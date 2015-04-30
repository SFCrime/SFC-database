from flask.ext.restful import Resource
from database_settings import EventModel, session
from geoalchemy2.shape import to_shape
import re

class Event(Resource):
    def get(self, event_id):
        try:
            res = session.query(EventModel).filter(
                EventModel.id_name == event_id).first()
            if res == None:
                raise AttributeError("No Event")
            
            res.start_time = str(res.start_time)
            res.end_time = str(res.end_time)
            res.end_date = str(res.end_date)
            res.start_date = str(res.start_date)
            print [x for x in vars(res).iteritems()]

            if res.shape_type == "polygon":
                res.shape = str(to_shape(res.shape))
                temp = re.findall(r"\(\((.*)\)\)", res.shape)
                t2 = temp[0].split(", ")
                t3 = [val.split(" ") for val in t2]
                res.shape_list = [[float(l1), float(l2)] for l1, l2 in t3]

            del(res._sa_instance_state)

            return dict(vars(res).iteritems()), 200

        except:
            session.rollback()
            return {}, 400

    def post(self, event_id):
        pass

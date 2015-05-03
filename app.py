#!/usr/bin/env python
from flask import Flask
from flask.ext.restful import Api
from flask.ext.cors import CORS
from resources.crime import Crime
from resources.event import Event


app = Flask(__name__)
cors = CORS(app, resources=r"/api/*", allow_headers="Content-Type",
            supports_credentials=True)
api = Api(app)

api_version = "/api/v1/"

crime_api = api_version + "crime/"
events_api = api_version + "events/"


api.add_resource(Crime, crime_api)
api.add_resource(Event, events_api + "<event_id>")

if __name__ == '__main__':
    app.run(debug=True)

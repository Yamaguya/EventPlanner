import sys
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

# Setup MongoDB connection
client = MongoClient('localhost', 27017)
db = client['calendar_db']
events_collection = db['events']

# Extends the Resource class from the flask_restful module
class Today(Resource):
    def get(self):
        today = datetime.now().strftime("%Y-%m-%d")
        events_today = list(events_collection.find({"date": today}))
        if events_today:
            return [event['description'] for event in events_today]
        else:
            return {"message": "There are no events for today!"}

class Event(Resource):
    def get(self, date):
        events_on_date = list(events_collection.find({"date": date}))
        if events_on_date:
            return [event['description'] for event in events_on_date]
        else:
            return {"message": f"There are no events for {date}!"}

    def post(self, date):
        parser = reqparse.RequestParser()
        parser.add_argument('event', required=True, help="Event description cannot be blank!")
        args = parser.parse_args()

        new_event = {"date": date, "description": args['event']}
        events_collection.insert_one(new_event)

        return {"message": f"Event added for {date}!"}, 201

    def delete(self, date):
        result = events_collection.delete_many({"date": date})
        if result.deleted_count > 0:
            return {"message": f"Events for {date} deleted!"}
        else:
            return {"message": f"No events found for {date}!"}, 404

# Define the routes
api.add_resource(Today, '/today')
api.add_resource(Event, '/event/<string:date>')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()

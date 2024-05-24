import sys
from flask import Flask, request, render_template, redirect, url_for
from flask_restful import Resource, Api, reqparse
from datetime import datetime
from pymongo import MongoClient

# Create Flask app instance
app = Flask(__name__)
api = Api(app)

##
# Setup MongoDB connection
# Connect to MongoDB server running on localhost at default port 27017
client = MongoClient('localhost', 27017)
# Access database 'calendar_db'
db = client['calendar_db']
# Access collection 'events' within 'calendar_db' database
events_collection = db['events']

@app.route('/')
def index():
    # Render the index.html Jinja template for the home page
    return render_template('index.html')

@app.route('/events', methods=['GET', 'POST'])
def events():
    # If the request method is POST, it means we are adding a new event
    # Get the date and event description from the form  
    if request.method == 'POST':
        date = request.form['date']
        event_desc = request.form['event']
        # Create a new event dictionary
        new_event = {"date": date, "description": event_desc}
        # Insert the new event into the MongoDB collection
        events_collection.insert_one(new_event)
        # Redirect the user back to the /events page to see the updated list
        return redirect(url_for('events'))
    
    # If the request method is GET, fetch all events from the MongoDB collection
    events = list(events_collection.find())
    # Render the events.html template and pass the events to it
    return render_template('events.html', events=events)

# Extends the Resource class from the flask_restful module
class Today(Resource):
    def get(self):
        # Get today's date in YYYY-MM-DD format
        today = datetime.now().strftime("%Y-%m-%d")
        # Find all events that match today's date
        events_today = list(events_collection.find({"date": today}))
        if events_today:
            # If there are events for today, return a list of their descriptions
            return [event['description'] for event in events_today]
        else:
            # If no events for today, return a message indicating so
            return {"message": "There are no events for today!"}

class Event(Resource):
    def get(self, date):
        # Find all events that match the specified date
        events_on_date = list(events_collection.find({"date": date}))
        if events_on_date:
            # If there are events on the specified date, return a list of their descriptions
            return [event['description'] for event in events_on_date]
        else:
            # If no events found for the specified date, return a message indicating so
            return {"message": f"There are no events for {date}!"}

    def post(self, date):
        # Parse the incoming request to get the event description
        parser = reqparse.RequestParser()
        parser.add_argument('event', required=True, 
                            help="Event description cannot be blank!")
        args = parser.parse_args()

        # Create a new event dictionary with the specified date and description
        new_event = {"date": date, "description": args['event']}
        # Insert the new event into the MongoDB collection
        events_collection.insert_one(new_event)
        # Return a message indicating that the event was added successfully
        return {"message": f"Event added for {date}!"}, 201

    def delete(self, date):
        # Delete all events that match the specified date
        result = events_collection.delete_many({"date": date})
        if result.deleted_count > 0:
            # If events were deleted, return a message indicating success
            return {"message": f"Events for {date} deleted!"}
        else:
            # If no events were found for the specified date, return a 404 message
            return {"message": f"No events found for {date}!"}, 404

# Define the routes for the API
api.add_resource(Today, '/today')
api.add_resource(Event, '/event/<string:date>')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()

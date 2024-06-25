# Import the dependencies.

# Flask
from flask import Flask, jsonify

# SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# datetime
import datetime as dt

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################


# Index route
@app.route("/")
def welcome():
    """List all available api routes."""
    return """Available Routes:<br/>
        /api/v1.0/precipitation<br/>
        /api/v1.0/stations<br/>
        /api/v1.0/tobs<br/>
        /api/v1.0/{start}<br/>
        /api/v1.0/{start}/{end}"""


# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the dates and temperature observations from the last year."""

    # Perform a query to retrieve the date and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= get_one_year_prior()).\
        all()

    # Create a dictionary from the row data and append to a list of
    # all_precipitation
    all_precipitation = []
    for date, prcp in results:
        all_precipitation.append({date: prcp})

    return jsonify(all_precipitation)


# Stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return all of the station names"""
    results = session.query(Station.station).all()
    return jsonify([station[0] for station in results])


# Temperatures route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of min, max, and avg temps for the most active station"""

    # Find the most active station
    most_active_id = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.tobs).desc()).\
        first()

    most_active_id = most_active_id[0]

    # Query the last 12 months of temperature observation data for the most
    # active station
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= get_one_year_prior()).\
        filter(Measurement.station == most_active_id).\
        all()

    # Save the query results as a list of dictionaries
    temps = [{"station": most_active_id},
             {"min_temp": results[1],
              "max_temp": results[2],
              "avg_temp": results[3]}]

    return jsonify(temps)


# Start date route
@app.route("/api/v1.0/<start>")
def start_date_only(start):
    """Return a list of min, max, and avg temps for a given start date"""
    results = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        first()

    temps = [{"start_date": start,
              "end_date": get_last_date().strftime("%Y-%m-%d")},
             {"min_temp": results[0],
              "max_temp": results[1],
              "avg_temp": results[2]}]

    return jsonify(temps)


# Start and end date route
@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):
    """Return a list of min, max, and avg temps for a given date range"""
    results = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        first()

    temps = [{"start_date": start,
              "end_date": end},
             {"min_temp": results[0],
              "max_temp": results[1],
              "avg_temp": results[2]}]

    return jsonify(temps)


# Helper functions

# Get last date in database
def get_last_date():
    """Return the last date in the database"""
    # set up dates based on database
    last_date = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).\
        first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')

    return last_date


def get_one_year_prior():
    """Return the date one year prior to the last date in the database"""
    last_date = get_last_date()
    one_year_prior = last_date - dt.timedelta(days=365)

    return one_year_prior


# Run the app
if __name__ == '__main__':
    app.run(debug=True)

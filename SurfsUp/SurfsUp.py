# Import the dependencies.
from flask import Flask, jsonify

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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

# set up dates based on database info
last_date = session.query(Measurement.date).\
    order_by(Measurement.date.desc()).\
    first()
last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')

one_year_prior = last_date - dt.timedelta(days=365)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    """List all available api routes."""
    return """Available Routes:<br/>
        /api/v1.0/precipitation<br/>
        /api/v1.0/stations<br/>
        /api/v1.0/tobs<br/>
        /api/v1.0/{start}<br/>
        /api/v1.0/{start}/{end}"""


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the dates and temperature observations from the last year."""

    # Perform a query to retrieve the date and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_prior).\
        all()

    # Create a dictionary from the row data and append to a list of
    # all_precipitation
    all_precipitation = []
    for date, prcp in results:
        all_precipitation.append({date: prcp})

    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def stations():
    """Return all of the station names"""
    results = session.query(Station.station).all()
    return jsonify([station[0] for station in results])


@app.route("/api/v1.0/tobs")
def tobs():
    most_data = session.query(Measurement.station,
                              func.count(Measurement.id)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).\
        first()

    station = most_data[0]

    results = session.query(Measurement.station,
                            func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).\
        filter(Measurement.station == station).\
        filter(Measurement.date >= one_year_prior).\
        first()

    temps = [{"station": station},
             {"min_temp": results[1],
              "max_temp": results[2],
              "avg_temp": results[3]}]

    return jsonify(temps)


@app.route("/api/v1.0/<start>")
def start_date_only(start):

    results = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        first()

    temps = [{"start_date": start,
              "end_date": last_date.strftime("%Y-%m-%d")},
             {"min_temp": results[0],
              "max_temp": results[1],
              "avg_temp": results[2]}]

    return jsonify(temps)


@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):
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


if __name__ == '__main__':
    app.run(debug=True)

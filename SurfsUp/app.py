# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################

# Create an instance of Flask
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (
        "<h1>Welcome to the Climate App!</h1>"
        "<h3>Date range 2010-01-01 and 2017-08-23"
        "<h2>Available Routes:</h2>"
        "<ul>"
        "<li><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a> - Precipitation data for the last year</li>"
        "<li><a href='/api/v1.0/stations'>/api/v1.0/stations</a> - List of weather stations</li>"
        "<li><a href='/api/v1.0/tobs'>/api/v1.0/tobs</a> - Temperature observations for the last year</li>"
        "<li><a>/api/v1.0/&lt;start&gt;</a> - Min, Avg, and Max temperatures since a given start date (enter date format YYYY-MM-DD)</li>"
        "<li><a>/api/v1.0/&lt;start&gt;/&lt;end&gt;</a> - Min, Avg, and Max temperatures between a start and end date(enter date format YYYY-MM-DD for both)</li>"
        "</ul>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in data set
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    
    # Perform query to retrieve last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= one_year_ago)\
        .all()

    # Convert results to dictionary with date as key and precipitation as value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Perform query to retrieve list of stations
    station_list = session.query(Station.station).all()
    stations = [station for station, in station_list]

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most active station for the previous year
    most_active_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count().desc())\
        .first()[0]
    
    # Calculate the date one year from the last date in data set
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    
    # Perform query to retrieve temperature observations for the most active station for the previous year
    temperature_data = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= one_year_ago)\
        .all()

    # Convert results to list of dictionaries
    temperature_list = [{"date": date, "tobs": tobs} for date, tobs in temperature_data]

    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Perform query to calculate TMIN, TAVG, and TMAX for dates greater than or equal to start date
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .first()

    # Convert results to dictionary
    temperature_dict = {"TMIN": temperature_stats[0], "TAVG": temperature_stats[1], "TMAX": temperature_stats[2]}

    return jsonify(temperature_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Perform query to calculate TMIN, TAVG, and TMAX for dates between start and end dates
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end)\
        .first()

    # Convert results to dictionary
    temperature_dict = {"TMIN": temperature_stats[0], "TAVG": temperature_stats[1], "TMAX": temperature_stats[2]}

    return jsonify(temperature_dict)

# Run the application
if __name__ == "__main__":
    app.run(debug=True)

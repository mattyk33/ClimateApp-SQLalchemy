import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
    return (f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;")

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    one_year_ago = dt.date(2017,8,23)-dt.timedelta(days=365)

    # Query for the dates and precipitation values
    precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=one_year_ago).all()

    # Create dictionary
    precip_dict = {}

    # Loop to add keys and values to dictionary
    for date, prcp in precip:
        precip_dict[date] = prcp

    session.close()

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session from Python to the DB
    session = Session(engine)

    # Create dictionary
    stations_dictionary = {}

    # Query all stations
    stat = session.query(Station.station, Station.name).all()
    for station, name in stat:
        stations_dictionary[station] = name

    session.close()
 
    return jsonify(stations_dictionary)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session from Python to the DB
    session = Session(engine)

    # Get the last date contained in the dataset and date from one year ago
    one_year_ago = dt.date(2017,8,23)-dt.timedelta(days=365)

    # Query for the dates and temperature values
    date_temps = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= one_year_ago).\
                order_by(Measurement.date).all()
    
    # Convert to list of dictionaries to jsonify
    tobs_list = []

    for date, tobs in date_temps:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict)

    session.close()

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_start(start):

    # Create our session from Python to the DB
    session = Session(engine)

    # Convert to list of dictionaries to jsonify
    temp_start_list = []

    # Query for ave, min, max
    temp_stats =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in temp_stats:
        temp_start_dict = {}
        temp_start_dict["Date"] = date
        temp_start_dict["TMIN"] = min
        temp_start_dict["TAVG"] = avg
        temp_start_dict["TMAX"] = max
        temp_start_list.append(temp_start_dict)

    session.close()    

    return jsonify(temp_start_list)
    

if __name__ == '__main__':
    app.run(debug=True)
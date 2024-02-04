# Import the dependencies.
from flask import Flask, jsonify
from datetime import datetime, timedelta
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import logging

logging.basicConfig

#################################################
# Database Setup
#################################################
# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`

Measurement = Base.classes.measurement
Station = Base.classes.station


# Create a session
def create_session():
    session = Session(engine)
    return session

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
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    start_date = datetime.strptime('2016-08-23', '%Y-%m-%d')
    end_date = datetime.strptime('2017-08-23', '%Y-%m-%d')

    # Query for precipitation data between the start and end dates
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    
    # Close the session
    session.close()
    # Convert to dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    # Convert into normal list
    stations_list = list(np.ravel(results))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_station_id = 'USC00519281'  # Adjust based on your analysis
    # Adjusted to use a specific date
    one_year_ago = datetime(2017, 8, 23) - timedelta(days=365)
    results = session.query(Measurement.tobs).\
              filter(Measurement.station == most_active_station_id).\
              filter(Measurement.date >= one_year_ago).all()
    session.close()

    # Convert list of tuples into normal list
    temps = list(np.ravel(results))
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end=None):
    session = create_session()

    if end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                  filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                  filter(Measurement.date >= start).all()
    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)

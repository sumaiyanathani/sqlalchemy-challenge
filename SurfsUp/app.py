import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
station = Base.classes.station
measurement = Base.classes.measurement


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
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end><br>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
 
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    
    sel = [measurement.prcp, measurement.date]
    precip_scores = session.query(*sel).\
    filter(measurement.date >= query_date).all()

    session.close()
    
    prec_dict = {}
    for precip, date in precip_scores:
        prec_dict[date] = precip

    return jsonify(prec_dict)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    results = session.query(measurement.station).distinct().all()
    
    session.close()
    
    all_stations = list(np.ravel(results))
    
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temps():
    
    session = Session(engine)
    
    results = session.query(measurement.tobs).\
    filter(measurement.date >= dt.date(2016, 8, 23)).\
    filter(measurement.station == 'USC00519281').all()

    session.close()
    
    temps_list = list(np.ravel(results))
    
    return jsonify(temps_list)


@app.route("/api/v1.0/<start>")
def start_date(start):
    
    ''' Calculates the minimum, maximum and average temperature for dates that are greater than or equal to the start date'''
    
    session = Session(engine)
    
    canonicalized = dt.datetime.strptime(start, "%Y-%m-%d").date()
    
    temps_from_start = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date >= canonicalized).all()
    
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    oldest_date = session.query(measurement.date).order_by(measurement.date).first()[0]
    
    session.close()
    
    most_recent_date_converted = dt.datetime.strptime(most_recent_date, "%Y-%m-%d").date()
    oldest_date_converted = dt.datetime.strptime(oldest_date, "%Y-%m-%d").date()
    
    temps_list = []
    if oldest_date_converted <= canonicalized <= most_recent_date_converted:
        for minimum, maximum, average in temps_from_start:
        
            temp_dict = {}
            temp_dict["minimum temperature"] = minimum
            temp_dict["maximum temperature"] = maximum
            temp_dict["average temperature"] = average
            temps_list.append(temp_dict)

        return jsonify(temps_list)
    
    else:
        return jsonify({"error": "Date not within range."})

    
@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start, end):
    
    ''' Calculates the minimum, maximum and average temperature for dates that are between the start date and end date'''
    
    session = Session(engine)
    
    canonicalized_start = dt.datetime.strptime(start, "%Y-%m-%d").date()
    canonicalized_end = dt.datetime.strptime(end, "%Y-%m-%d").date()
    
    temperatures = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date >= canonicalized_start).\
    filter(measurement.date <= canonicalized_end).all()
    
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    oldest_date = session.query(measurement.date).order_by(measurement.date).first()[0]
    
    session.close()
    
    most_recent_date_converted = dt.datetime.strptime(most_recent_date, "%Y-%m-%d").date()
    oldest_date_converted = dt.datetime.strptime(oldest_date, "%Y-%m-%d").date()
    
    temps_list = []
    if (oldest_date_converted <= canonicalized_start <= most_recent_date_converted) and (oldest_date_converted <= canonicalized_end <= most_recent_date_converted):
        for minimum, maximum, average in temperatures:
        
            temp_dict = {}
            temp_dict["minimum temperature"] = minimum
            temp_dict["maximum temperature"] = maximum
            temp_dict["average temperature"] = average
            temps_list.append(temp_dict)

        return jsonify(temps_list)
    
    else:
        return jsonify({"error": "Either start date, stop date or both not within range."})
    

if __name__ == '__main__':
    app.run(debug=True)
    
    

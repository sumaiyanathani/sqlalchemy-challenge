# Importing dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Creating engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflecting an existing database into a new model
Base = automap_base()

# Reflecting the tables
Base.prepare(autoload_with=engine)


# Saving references to each table
station = Base.classes.station
measurement = Base.classes.measurement


# Setting up Flask
app = Flask(__name__)


# Defining Welcome page 
@app.route("/")
def welcome():
    """Lists all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end><br>"
    )


# Defining precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Creating session (link)
    session = Session(engine)
    
    # Getting the query date to be used in the query
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    
    # Selecting the required arrtibutes or columns for the query and filtering based on the query date
    sel = [measurement.prcp, measurement.date, measurement.station]
    precip_scores = session.query(*sel).\
    filter(measurement.date >= query_date).\
    filter(measurement.station == station.station).all()
    
    # Closing the session
    session.close()
    
    # Making an empty dictionary and for each date as the key, adding a list of temperatures corresponding to that date from various stations as the value using a for loop
    prec_dict = {}
    for precip, date, stn in precip_scores:
        if date in prec_dict.keys():
            prec_dict[date].append(precip)
        else:
            prec_dict[date] = [precip]

    #Returning the JSON representation of prec_dict dictionary
    return jsonify(prec_dict)


# Defining stations route
@app.route("/api/v1.0/stations")
def stations():
    
    # Creating session (link)
    session = Session(engine)
    
    # Retrieving all the distinct station names
    results = session.query(measurement.station).distinct().all()
    
    # Closing the session
    session.close()
    
    # Getting the stations by converting the list of tuples to a list
    all_stations = list(np.ravel(results))
    
    # Returning a JSON list of stations from the dataset 
    return jsonify(all_stations)


# Defining temperatures route
@app.route("/api/v1.0/tobs")
def temps():
    
    # Creating session (link)
    session = Session(engine)
    
    # Retrieving the observed temperatures of the most-active station for the previous year of data
    results = session.query(measurement.tobs).\
    filter(measurement.date >= dt.date(2016, 8, 23)).\
    filter(measurement.station == 'USC00519281').all()
    
    # Closing the session
    session.close()
    
    # Getting the temperatures by converting the list of tuples to a list
    temps_list = list(np.ravel(results))
    
    # Returning a JSON list of temperatures observed for the previous year
    return jsonify(temps_list)


# Defining start date route
@app.route("/api/v1.0/<start>")
def start_date(start):
    
    # Creating session (link)
    session = Session(engine)
    
    # Converting the start date given by user to a datetime date to use in query
    canonicalized = dt.datetime.strptime(start, "%Y-%m-%d").date()
    
    # Calculating the minimum, maximum and average temperature for dates that are greater than or equal to the start date from query
    temps_from_start = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date >= canonicalized).all()
    
    # Finding the most recent and oldest dates in the database so that the start date inputted by the users is not above the most recent date and not below the oldest date
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    oldest_date = session.query(measurement.date).order_by(measurement.date).first()[0]
    
    # Closing the session
    session.close()
    
    # Converting the most recent and oldest date to datetime date
    most_recent_date_converted = dt.datetime.strptime(most_recent_date, "%Y-%m-%d").date()
    oldest_date_converted = dt.datetime.strptime(oldest_date, "%Y-%m-%d").date()
    
    # Creating an empty list to populate minimum, maximum and average temperature data from the query results
    temps_list = []
    
    # Creating an if statement to remain within the range of the most recent and oldest date
    if oldest_date_converted <= canonicalized <= most_recent_date_converted:
        
        # Creating for loop to add the minimum, maximum and average temperature data to a dictionary first and then to appending it to a list
        for minimum, maximum, average in temps_from_start:
        
            temp_dict = {}
            temp_dict["minimum temperature"] = minimum
            temp_dict["maximum temperature"] = maximum
            temp_dict["average temperature"] = average
            temps_list.append(temp_dict)
        
        # Returning a JSON list of the temperature data
        return jsonify(temps_list)
    
    # Else if the date inputted by the user is not within the range of the dates within the dataset, this error message will appear
    else:
        return jsonify({"error": "Date not within range."})

    
# Defining start date and end date route
@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start, end):
    
    # Creating session (link)
    session = Session(engine)
    
    # Converting the start date and end date given by user to a datetime date to use in query
    canonicalized_start = dt.datetime.strptime(start, "%Y-%m-%d").date()
    canonicalized_end = dt.datetime.strptime(end, "%Y-%m-%d").date()
    
    # Calculating the minimum, maximum and average temperature for dates that are between the start date and end date from query
    temperatures = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date >= canonicalized_start).\
    filter(measurement.date <= canonicalized_end).all()
    
    # Finding the most recent and oldest dates in the database so that the start date inputted by the users is not above the most recent date and not below the oldest date
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    oldest_date = session.query(measurement.date).order_by(measurement.date).first()[0]
    
    # Closing the session
    session.close()
    
    # Converting the most recent and oldest date to datetime date
    most_recent_date_converted = dt.datetime.strptime(most_recent_date, "%Y-%m-%d").date()
    oldest_date_converted = dt.datetime.strptime(oldest_date, "%Y-%m-%d").date()
    
    # Creating an empty list to populate minimum, maximum and average temperature data from the query results
    temps_list = []
    
    # Creating an if statement to keep the start and end dates within the range of the most recent and oldest date
    if (oldest_date_converted <= canonicalized_start <= most_recent_date_converted) and (oldest_date_converted <= canonicalized_end <= most_recent_date_converted):
        
        # Creating for loop to add the minimum, maximum and average temperature data to a dictionary first and then to appending it to a list
        for minimum, maximum, average in temperatures:
        
            temp_dict = {}
            temp_dict["minimum temperature"] = minimum
            temp_dict["maximum temperature"] = maximum
            temp_dict["average temperature"] = average
            temps_list.append(temp_dict)

        # Returning a JSON list of the temperature data
        return jsonify(temps_list)
    
    # Else if the date(s) inputted by the user is not within the range of the dates within the dataset, this error message will appear
    else:
        return jsonify({"error": "Either start date, stop date or both not within range."})
    
# Running the app with the debugger set to True so that errors can be identified
if __name__ == '__main__':
    app.run(debug=True)
    
    

from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"<br>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    #Convert the query results to a Dictionary using date as the key and prcp as the value.
    
    date_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    last_1year = dt.date(2017,8,23) - dt.timedelta(days= 365)

    prcp_data_query = session.query(Measurement.date, Measurement.prcp).\
                      filter(Measurement.date >= last_1year, Measurement.prcp != None).\
                    order_by(Measurement.date).all()

    #Return the JSON representation of your dictionary.
    return jsonify(dict(prcp_data_query))

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    active_stations = session.query(Measurement.station,func.count(Measurement.station)).\
                               group_by(Measurement.station).\
                               order_by(func.count(Measurement.station).desc()).all()
    
    
    #Return a JSON list of stations from the dataset.
    return jsonify(dict(active_stations))


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    #query for the dates and temperature observations from a year from the last data point
    #last_1year = dt.date(2017,8,23) - dt.timedelta(days= 365)
    tobs_1year  = session.query(Measurement.tobs, Measurement.date).\
                                    filter(Measurement.date >='2016-08-23', Measurement.date <='2017-08-23').all()

    tobs_list=[]

    for tob in tobs_1year:
        tobs_list.append(tob._asdict())
        
    resp_dict={}        
    resp_dict['response'] = tobs_list                                
    #Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(resp_dict)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine) 
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    Tmin_avg_max =session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).all()

    result={'TMin':Tmin_avg_max[0][0],
    'TAvg':Tmin_avg_max[0][1],
    'TMax':Tmin_avg_max[0][2]
    }

    return jsonify(result)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine) 
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for given date range
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    Tmin_avg_max =session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start, Measurement.date <= end, ).all()

    result={'TMin':Tmin_avg_max[0][0],
    'TAvg':Tmin_avg_max[0][1],
    'TMax':Tmin_avg_max[0][2]
    }

    return jsonify(result)

if __name__ == "__main__":

    app.run(debug=True)

#@app.route("/api/v1.0/<start>/<end>")
    

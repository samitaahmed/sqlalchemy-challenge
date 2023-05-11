# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect,desc
import numpy as np
from flask import Flask,jsonify
import os


#################################################
# Database Setup
#################################################
dir_path = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(dir_path, "Resources/hawaii.sqlite")
engine = create_engine(f"sqlite:///{db_file}") 
# reflect an existing database into a new model

# reflect the tables
Base = automap_base()
Base.prepare(autoload_with = engine)

# Save references to each table


measurement = Base.classes.measurement
station = Base.classes.station
# Create our session (link) from Python to the DB



#################################################
# Flask Setup
#################################################

app = Flask(__name__)
@app.route("/")
def home():
    """List of all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date (YYYY-MM-DD)<br/>"
        f"/api/v1.0/start_date (YYYY-MM-DD)/end_date (YYYY-MM-DD)<br/>"
     
    )
#################################################
# Flask Routes
#################################################


@app.route("/api/v1.0/precipitation")
def Precipitation():
    """ precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value."""
    session = Session(engine)
    maxdate = session.query(measurement.date).order_by(desc(measurement.date)).first()
    date_object = dt.datetime.strptime(maxdate[0], '%Y-%m-%d').date()-dt.timedelta(days=365)
    prcp_info = session.query(measurement.date,measurement.prcp).filter(measurement.date >= date_object).all()

    session.close()

    prcp_dict = dict(prcp_info)

    prcp_list = [{"date": d, "prcp": p} for d, p in prcp_dict.items()]

    return jsonify(prcp_list)



@app.route("/api/v1.0/stations")
def Stations():
    """ Return a JSON list of stations from the dataset."""
    session = Session(engine)
    
    station_count = session.query(station.station).count()

    session.close()


    return f" Total number of stations: {station_count}"


@app.route("/api/v1.0/tobs")
def tobs():
    """ dates and temperature observations of the most-active station for the previous year of data."""
    session = Session(engine)
    maxdate = session.query(measurement.date).order_by(desc(measurement.date)).first()
    date_object = dt.datetime.strptime(maxdate[0], '%Y-%m-%d').date()-dt.timedelta(days=365)
    s = func.count(measurement.station)
    Active_stations = session.query(measurement.station,s).group_by(measurement.station).order_by(s.desc()).all()
    tobs_info = session.query(measurement.date,measurement.tobs).filter(measurement.date >= date_object).filter(measurement.station== Active_stations[0][0]).all()

    session.close()

    tobs_dict = dict(tobs_info)

    tobs_list = [{"date": d, "temperature": t} for d, t in tobs_dict.items()]

    return jsonify(tobs_list)



@app.route("/api/v1.0/<startdate>/<end>")
def startandend(startdate,end):
    """ Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""
    session = Session(engine)
    min_date = dt.datetime.strptime(startdate, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    tob_info = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).all()


    session.close()

    tob_dict = {'Minimum Temperature': tob_info[0][0], 'Maximum Temperature': tob_info[0][1], 'Average Temperature: ':tob_info[0][2]}

  
    return jsonify(tob_dict)

@app.route("/api/v1.0/<start>")
def startdate(start):
    """ Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""
    session = Session(engine)
    
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    tob_info = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date >= start_date).all()
    
    session.close()

    tob_dict = {'Minimum Temperature': tob_info[0][0], 'Maximum Temperature': tob_info[0][1], 'Average Temperature: ':tob_info[0][2]}

    return jsonify(tob_dict)

if __name__ == '__main__':
    app.run(debug=True)


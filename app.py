import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources//hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup

app = Flask(__name__)

#  List all routes that are available
@app.route("/")
def welcome():
    return (      
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start --> Input date as: YYYY-MM-DD<br/>"
        f"/api/v1.0/temp/start/end --> Input date as: YYYY-MM-DD<br/>"
    )

# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precip():
    """Return the date_orcp data as json"""
    session = Session(engine)  
    last_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    result = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=last_year).all()

    session.close()
    return jsonify(result)
    

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/station")
def station():
    session = Session(engine)  
    """Return the date_orcp data as json"""
    station_result = session.query(Measurement.station,func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    session.close()
    return jsonify(station_result)

#Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)  
    last_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    temp_result=session.query(Measurement.tobs).\
            filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date>=last_year).all()
    temps=list(np.ravel(temp_result))
    session.close()
    return jsonify(temps)

#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.@app.route('/api/v1.0/temp/<start>')

@app.route('/api/v1.0/temp/<start>/<end>')
def temp(start=None, end=None):
    session = Session(engine)  
    sel=[func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)]
    if not end:
        result=session.query(*sel).filter(Measurement.date>=start).all()
        temperature=list(np.ravel(result))
        session.close()
        return jsonify(temperature)
    result=session.query(*sel).filter(Measurement.date>=start).filter(Measurement.date<=end).all()
    temperature=list(np.ravel(result))
    session.close()
    return jsonify(temperature)

if __name__ == "__main__":
    app.run(debug=True)
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from sense_hat import SenseHat

sense = SenseHat()

def sense_data(sea_state_span_sec):
    ##Track orientation data over a set timelimit to measure seastate
    orientation = pd.DataFrame(columns = ['roll', 'pitch', 'yaw'])
    time_start = datetime.now()

    while datetime.now() <= (time_start + timedelta(0,sea_state_span_sec)):
        orientation = orientation.append(sense.get_orientation(), ignore_index = True)

    orientation_delta = np.sin(np.deg2rad(orientation))*180/np.pi

    roll_mean = round(np.mean(orientation_delta["roll"]), 0)
    pitch_mean = round(np.mean(orientation_delta["pitch"]), 0)   
    yaw_mean = round(np.mean(orientation_delta["yaw"]),0)

    roll_sd = round(np.std(orientation_delta["roll"]), 0)
    pitch_sd = round(np.std(orientation_delta["pitch"]), 0)
    yaw_sd = round(np.std(orientation_delta["yaw"]), 0)
    volatility = max(roll_sd, pitch_sd, yaw_sd)

    ## Pull in the rest of the sensor data
    # Read the sensors
    temp_c = sense.get_temperature()
    humidity = sense.get_humidity() 
    pressure_mb = sense.get_pressure()
    mag = sense.get_compass()

    # Format the data
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    temp_f = float(round(temp_f,0))
    humidity = float(round(humidity,0))
    pressure_mb = float(round(pressure_mb,0))
    mag = float(round(mag,0))

    # Collate data with labels
    sh_data = {
        "Temperature (F)": temp_f,
        "Humidity (%)": humidity,
        "Pressure (mb)": pressure_mb,
        "Compass Heading": mag,
        "Roll (deg)": roll_mean,
        "Pitch (deg)": pitch_mean,
        "Yaw (deg)": yaw_mean,
        "Roll StDev (deg)": roll_sd,
        "Pitch StDev (deg)": pitch_sd,
        "Yaw StDev (deg)": yaw_sd,
        "Volatility": volatility
        }

    return(sh_data)

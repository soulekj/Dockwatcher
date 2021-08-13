import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from sense_hat import SenseHat
from math import radians, cos, sin, asin, sqrt
import feedparser as fp
import gps
import time
from ISStreamer.Streamer import Streamer


# SENSE_DATA
# pulls sensor data from raspberry pi SenseHat

sense = SenseHat()

def sense_data(sea_state_span_sec, temp_correction):
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
    temp_f = temp_c * 9.0 / 5.0 + 32.0 + temp_correction
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


# GET_GPS
# custom function to try to pull GPS fix from USB GPS

def get_gps(timeout):
    
    #create dictionary to store gps data
    gps_data = {
        "Lat": None,
        "Lon": None
    }

    #open gps nmea stream
    gpsd = gps.gps()
    gpsd.stream(gps.WATCH_ENABLE|gps.WATCH_NEWSTYLE)

    #keep checking for gps status until a fix can be made or until timeout is reached
    gps_status = 0
    i = 0
    while (gps_status == 0) & (i < timeout) & (gpsd.status != 0):
        try:
            for report in gpsd: 
                if report['class'] == 'TPV':
                    gps_data['Lat'] = report['lat']
                    gps_data['Lon'] = report['lon']
                    gps_status = 1
                    break
        except: 
            gps_status = 0
            i = i+1
            time.sleep(1) #pause 1 second between retrying

    return(gps_data)


#HAVERSINE
#custom function that calculates the distance between two positions on the globe

def haversine(lon1, lat1, lon2, lat2):
    #convert degrees to radians
    lon1 = radians(lon1)
    lat1 = radians(lat1)
    lon2 = radians(lon2)
    lat2 = radians(lat2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    #haversine formula
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    distance = 2 * asin(sqrt(a)) * 3440.1 # is radius of Earth in nm

    return distance


# NOAA_BUOY
# custom function to pull the weather data from the closest NOAA weather buoy

def noaa_buoy(LAT, LON, DIRECTORY):
    
    #read in csv data
    buoy_list = pd.read_csv(DIRECTORY + 'Data/' + 'NDBC_Buoy_List.csv')
    buoy_list = buoy_list[buoy_list["met"] == 'y']
    
    #find the closet buoy on NOAA's list
    smallest = 21369              #circumference of earth of nm 
    for ind in buoy_list.index:
        buoy_lon = buoy_list['lon'][ind]
        buoy_lat = buoy_list['lat'][ind]
        distance = haversine(LON, LAT, buoy_lon, buoy_lat)
        if distance < smallest:
            smallest = distance
            closest = buoy_list['id'][ind]
    buoy_name = closest
    buoy_dist = round(float(smallest),1)
    
    #scrape the buoy data from NOAA's website
    buoy_data = fp.parse('https://www.ndbc.noaa.gov/data/latest_obs/' + buoy_name + '.rss')
    entry = buoy_data.entries[0]
    buoy_raw = entry.summary.replace('<strong>', '').replace('</strong>', '')
    
    #Timestamp
    ts_end = buoy_raw.index('<br />')
    buoy_ts = buoy_raw[0:ts_end]
    
    #location
    loc_start = buoy_raw.index('Location: ') + 10
    loc_end = buoy_raw[loc_start:].index('<br />') + loc_start
    buoy_loc = buoy_raw[loc_start:loc_end]
    
    #wind direction
    try:
        wd_start = buoy_raw.index('Wind Direction: ') + 16
        wd_end = buoy_raw[wd_start:].index('<br />') + wd_start
        buoy_wd = buoy_raw[wd_start:wd_end]
        buoy_wd_deg = float(buoy_wd[buoy_wd.index('(')+1:buoy_wd.index('&')])
    except:
        buoy_wd_deg = None
    
    #Wind Speed
    try:
        wspd_start = buoy_raw.index('Wind Speed: ') + 12
        wspd_end = buoy_raw[wspd_start:].index('<br />') + wspd_start
        buoy_wspd = buoy_raw[wspd_start:wspd_end]
        buoy_wspd_kts = float(buoy_wspd[0:buoy_wspd.index(' ')])
    except: buoy_wspd_kts = None
    
    #Wind Gust
    try:
        wgst_start = buoy_raw.index('Wind Gust: ') + 11
        wgst_end = buoy_raw[wgst_start:].index('<br />') + wgst_start
        buoy_wgst = buoy_raw[wgst_start:wgst_end]
        buoy_wgst_kts = float(buoy_wgst[0:buoy_wgst.index(' ')])
    except: buoy_wgst_kts = None

    #Atmospheric Pressure
    try:
        atm_start = buoy_raw.index('Atmospheric Pressure: ') + 22
        atm_end = buoy_raw[atm_start:].index('<br />') + atm_start
        buoy_atm = buoy_raw[atm_start:atm_end]
        buoy_atm_mb = float(buoy_atm[buoy_atm.index('(')+1:buoy_atm.index(' mb')])
    except: buoy_atm_mb = None

    #Air Temperature
    try:
        temp_start = buoy_raw.index('Air Temperature: ') + 17
        temp_end = buoy_raw[temp_start:].index('<br />') + temp_start
        buoy_temp = buoy_raw[temp_start:temp_end]
        buoy_temp_F = float(buoy_temp[0:buoy_temp.index('&')])
    except: buoy_temp_F = None

    #Dew Point
    try:
        dpt_start = buoy_raw.index('Dew Point: ') + 11
        dpt_end = buoy_raw[dpt_start:].index('<br />') + dpt_start
        buoy_dpt = buoy_raw[dpt_start:dpt_end]
        buoy_dpt_F = float(buoy_dpt[0:buoy_temp.index('&')])
    except: buoy_dpt_F = None
    
    #Visibility
    try:
        viz_start = buoy_raw.index('Visibility: ') + 12
        viz_end = buoy_raw[viz_start:].index('<br />') + viz_start
        buoy_viz = buoy_raw[viz_start:viz_end]
        buoy_viz_nm = float(buoy_viz[0:buoy_viz.index(' ')])
    except: buoy_viz_nm = None
    
    buoy_dict = {
    "Name": buoy_name.upper() +' (' + str(buoy_dist) + ' nm away)',
    "Timestamp": buoy_ts,
    "Location": buoy_loc,
    "Wind Direction (o)": buoy_wd_deg,
    "Wind Speeds (kts)": buoy_wspd_kts,
    "Wind Gusts (kts)": buoy_wgst_kts,
    "Pressure (mb)": buoy_atm_mb,
    "Temperature (F)": buoy_temp_F,
    "Dew Point (F)": buoy_dpt_F,
    "Visibility (nm)": buoy_viz_nm
    }
    
    return buoy_dict
    

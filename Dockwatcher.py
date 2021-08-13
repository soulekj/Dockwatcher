# ------------------------------- DOCKWATCHER --------------------------------


# Notes ----------------------------------------------------------------------

# To do
## configure alarms / alerts (within initial sync)
## Add in logic for correcting for temperature

# Change Log:
## 2021.08.10 - updated to only run once, and then crontab set to regularly run file
## 2021.08.11 - made all settings callable a file, and all custom functions callable from a file

# ----------------------------------------------------------------------------


# Setup
from Settings import *     #import initialization parameters
from Packages import *     #import packages and custom defined functions


#Import data from SenseHat
sh_snapshot = sense_data(SEA_STATE_SPAN_SEC, TEMP_CORRECTION)


# Import data from GPS, and if a fix is made, update location
gps_loc = get_gps(GPS_FIX_SEC)                                      
if (gps_loc['Lat'] != None) & (gps_loc['Lon'] != None):
    CURRENT_LAT = gps_loc['Lat']
    CURRENT_LON = gps_loc['Lon']
loc_coord_str = {
    "Location": str(CURRENT_LAT) + "N, " + str(CURRENT_LON*(-1)) + "W"      #Assumes always in NW hemisphere
    }


#Import data from NOAA buoy
buoy_snapshot = noaa_buoy(CURRENT_LAT, CURRENT_LON, DIRECTORY)


#Create a summary tag to characterizes this reading on the dashboard
readings = {
    "Boat": 'Boat Snapshot from ' + datetime.now().strftime("%B %d %Y, %H:%M") + " " + str(datetime.now().strftime("%r"))[9].lower() + "m EST",
    "Buoy": 'NOAA Buoy Snapshot from ' + buoy_snapshot['Timestamp']
    }


#Send data to InitialState
streamer = Streamer(bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)
streamer.log_object(loc_coord_str, key_prefix = "Boat ")
streamer.log_object(sh_snapshot, key_prefix = "Boat ")
streamer.log_object(buoy_snapshot, key_prefix = "Buoy ")
streamer.log_object(readings, key_prefix = "Readings ")
streamer.flush()

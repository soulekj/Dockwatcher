##to do
#troubleshoot why force quits happen (NOAA BUOY SCRIPT)
#generate buoy list if it doesn't exist already
#synchronize pi clock with gps clock
#add in weather forecast details
#configure alarms / alerts (within initial sync)
#Make user settings a separate text file
#Make sure only to pull in weather buoy data from buoy that is reporting wind
#Define streaming as a function and have option to overide internal GPS with preset coordinates
#Add in logic for correcting for temperature


import time  
import sys
from datetime import datetime
from ISStreamer.Streamer import Streamer  
from sensehat_data import sense_data        #custom function
from noaa_buoy_data import noaa_buoy        #custom function
from gps_data import get_gps                #custom function


# --------- User Settings ---------
BUCKET_NAME = "Aurora Dock-Watcher"
BUCKET_KEY = "K6S8MB67WJLS"
ACCESS_KEY = "ist_47mQx4kg8OSYyh1l-k8atYDGJSM2SglH"
MINUTES_BETWEEN_SENSEHAT_READS = .5
SEA_STATE_SPAN_SEC = 10
GPS_FIX_SEC = 30

CURRENT_LAT = 41.77  #default values for Providence, will be updated after first fix
CURRENT_LON = -71.39 #default values for Providence, will be updated after first fix
# ---------------------------------


#streamer = Streamer(bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)

#while True:
i = 1
while i == 1:
    #Import location from GPS, and a fix is made, update location
    gps_loc = get_gps(GPS_FIX_SEC)                                      #Number is the timeout for finding a GPS fix
    if (gps_loc['Lat'] != None) & (gps_loc['Lon'] != None):
        CURRENT_LAT = gps_loc['Lat']
        CURRENT_LON = gps_loc['Lon']
    loc_coord_str = {
        "Location": str(CURRENT_LAT) + "N, " + str(CURRENT_LON*(-1)) + "W"      #Assumes always in NW hemisphere
        }
    
    #Import data from SenseHat
    sh_snapshot = sense_data(SEA_STATE_SPAN_SEC)
    
    #Import data from NOAA buoy
    buoy_snapshot = noaa_buoy(CURRENT_LAT, CURRENT_LON)

    #Create a summary tag to characterizes this reading
    readings = {
        "Boat": 'Boat: ' + datetime.now().strftime("%B %d %Y, %H:%M") + " " + str(datetime.now().strftime("%r"))[9].lower() + "m EST",
        "Buoy": buoy_snapshot['Name'] + ': ' + buoy_snapshot['Timestamp']
        }
    
    #Stream data
#    streamer.log_object(loc_coord_str, key_prefix = "Boat ")
#    streamer.log_object(sh_snapshot, key_prefix = "Boat ")
#    streamer.log_object(buoy_snapshot, key_prefix = "Buoy ")
#    streamer.log_object(readings, key_prefix = "Readings ")

    #Wait between snapshots
#    streamer.flush()
    
#    time.sleep(60*MINUTES_BETWEEN_SENSEHAT_READS - SEA_STATE_SPAN_SEC)

    print(sh_snapshot)
    
    i = i+1

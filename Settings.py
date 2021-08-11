# Installation Directory
DIRECTORY = "/home/pi/Documents/Dockwatcher/"  #needs to be where the NOAA BUOY data files are stored

#Initial State Connection Parameters
BUCKET_NAME = "Aurora Dock-Watcher"
BUCKET_KEY = "K6S8MB67WJLS"
ACCESS_KEY = "ist_47mQx4kg8OSYyh1l-k8atYDGJSM2SglH"

#Dockwatcher Timing Parameters
SEA_STATE_SPAN_SEC = 10     #amount of time over which the sea state is monitored
GPS_FIX_SEC = 30            #max amount of time the dockwatcher should look for a GPS fix

#Default location parameters (will be updated to true location after first GPS fix)
CURRENT_LAT = 41.77         #Providence Latitude
CURRENT_LON = -71.39        #Providence Longitude
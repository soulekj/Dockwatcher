import gps
import time

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

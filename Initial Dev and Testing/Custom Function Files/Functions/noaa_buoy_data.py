##To do:
#add error handeling for import table, with code to generate it if there is an issue
#make sure the "None" values get passed to initialstate correctly when buoy isn't reporting all fields
#Make sure only to pull in weather buoy data from buoy that is reporting wind

from requests import get
import pandas as pd
import feedparser as fp
from haversine import haversine

def noaa_buoy(LAT, LON, DIRECTORY):
    
    #read in csv data
    buoy_list = pd.read_csv(DIRECTORY + 'Program Files/Data/' + 'NDBC_Buoy_List.csv')
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

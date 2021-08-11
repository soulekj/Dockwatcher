from requests import get
import xml.etree.ElementTree as ET 
import pandas as pd

root = ET.fromstring(get('https://www.ndbc.noaa.gov/activestations.xml').text)
buoy_list = pd.DataFrame(columns = root[0].attrib.keys())
for entry in root:
    buoy_list = buoy_list.append(entry.attrib, ignore_index = True)
buoy_list.to_csv('NDBC_Buoy_List.csv', index=False)

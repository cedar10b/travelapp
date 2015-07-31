# -*- coding: utf-8 -*-

import requests
import json
import numpy as np
import pandas as pd
from sql_functions import *
from requests.packages import urllib3
urllib3.disable_warnings()

try:
  airfare = read_table('airfare')
except:  
  # load city and airport data
  cities = read_table('cities')
  airports = read_table('airports')
  
  # merge city and airport data and create column to store airfares
  airfare = cities.ix[:, ['city', 'state_abbr']]
  airfare = pd.merge(airfare, airports.ix[:,['city', 'state_abbr', 'airport_code']], 
                     on=['city', 'state_abbr'], how='left')
  airfare['airfare'] = np.nan

# find unique airport codes to search for airfares
codes = airfare.ix[0:99].airport_code.unique() #73 unique codes


# collect airfare data
# check this link for the documentation of the QPX Express API
#https://developers.google.com/resources/api-libraries/documentation/qpxExpress/v1/python/latest/qpxExpress_v1.trips.html
# check also google developers console:
# https://console.developers.google.com/project/mystic-hull-101406/apiui/credential#
api_key = 'AIzaSyD0k6jBvCkbKPW-uIslmOl8G8WH6s7inh4'
url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=" + api_key
headers = {'content-type': 'application/json'}

tickets = []
for i in range(0,50):
  print 'collecting data for ', airfare[airfare.airport_code == codes[i]].iloc[0,0]
  params = {"request": 
               {"slice":     
                               [{"origin":        "SFO",
                                 "destination":   codes[i],
                                 "date":          "2015-07-31",
                                 "earliestTime":  "17:00",
                                 "maxConnectionDuration": 180},
                                {"origin":        codes[i],
                                 "destination":   "SFO",
                                 "date":          "2015-08-02",
                                 "earliestTime":  "15:00",
                                 "maxConnectionDuration": 180}],
               "passengers":   { "adultCount":    1},
               "solutions":    1, 
               "refundable":   False}}
  response = requests.post(url, data=json.dumps(params), headers=headers)
  data = response.json()
  tickets.append(data)
  total_fare = float(data['trips']['tripOption'][0]['saleTotal'][3:])
  airfare.ix[airfare.airport_code == codes[i], 'airfare'] = total_fare

create_table(airfare, 'airfare')



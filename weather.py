# -*- coding: utf-8 -*-you

import urllib2
import json
import pandas as pd
import numpy as np
from sql_functions import *


day = 1
month = 8

# find which of the returned 10 forecasts corresponds to next Saturday
def find_record(parsed_json, day=day, month=month):
  for i in range(10):
    iday = parsed_json['forecast']['simpleforecast']['forecastday'][i]['date']['day']
    imonth = parsed_json['forecast']['simpleforecast']['forecastday'][i]['date']['month']    
    if (iday == day) and (imonth == month):
      return parsed_json['forecast']['simpleforecast']['forecastday'][i]

# read cities table and create new table to store weather data
cities = read_table('cities')
weather = pd.DataFrame([], columns = ['city', 'state_abbr', 'mintemp',
                       'maxtemp', 'humidity', 'wind', 'condition'])

# download weather data from wunderground
for i in range(100):
  city = '_'.join(cities.city[i].split(' '))
  state = cities.state_abbr[i]
  print 'downloading data for ', city, state
  f = urllib2.urlopen('http://api.wunderground.com/api/b0737287e2cf0580/forecast10day/q/' \
                      + state + '/' + city + '.json')
  json_string = f.read()
  f.close()
  parsed_json = json.loads(json_string)
  data = find_record(parsed_json, day, month)
  mintemp = data['low']['fahrenheit']
  maxtemp = data['high']['fahrenheit']
  humidity = data['avehumidity']
  wind = data['avewind']['mph']
  condition = data['conditions']
  row = {'city': cities.city[i], 'state_abbr': cities.state_abbr[i], 
         'mintemp': mintemp, 'maxtemp': maxtemp, 
         'humidity': humidity, 'wind': wind, 'condition': condition}
  weather = weather.append(row, ignore_index=True)

# check the description phrases at:  
# http://www.wunderground.com/weather/api/d/docs?d=resources/phrase-glossary&MR=1
condition_dict = {'excellent': ['Clear', 'Sunny', 'Mostly Sunny', 'Scattered Clouds'],
                  'good': ['Partly Sunny', 'Partly Cloudy', 'Mostly Cloudy', 'Cloudy',
                           'Haze', 'Overcast', 'Fog'],
                  'bad': ['Rain', 'Chance of a Thunderstorm', 'Chance of Thunderstorms',
                          'Chance of Snow', 'Chance of Sleet', 'Chance of Freezing Rain',
                          'Chance Rain', 'Chance of Rain', 'Chance of Flurries'],
                  'terrible': ['Thunderstorm', 'Thunderstorms', 'Snow', 'Sleet',
                               'Freezing Rain', 'Flurries']}
  
def compute_score(weather):
  total_score = -np.ones(weather.shape[0])
  for i in range(weather.shape[0]):
    mintemp = float(weather.ix[i, 'mintemp'])
    maxtemp = float(weather.ix[i, 'maxtemp'])
    humidity = float(weather.ix[i, 'humidity'])
    wind = float(weather.ix[i, 'wind']) 
    condition = weather.ix[i, 'condition']
    
    # process temperature data
    idealT = 73.    
    dev = np.sqrt(0.5*(abs(idealT - mintemp)**2 + abs(idealT - maxtemp)**2))
    if (dev <= 10.):    
      Tscore = 1.
    elif (dev >= 50):
      Tscore = 0.
    else:
      Tscore = 1. - (dev - 10.)/40.
    
    # process humidity data
    idealH = 45
    if abs(humidity - idealH) <= 15:
      Hscore = 1.
    elif (humidity - idealH) > 15. and (humidity - idealH) <= 45.:
      Hscore = 0.9
    elif (idealH - humidity) > 15. and (idealH - humidity) <= 35.:
      Hscore = 0.9
    elif (humidity - idealH) > 45. or (idealH - humidity) > 35.:
      Hscore = 0.8
      
    if ((humidity - idealH) > 35.) and (0.5*(maxtemp + mintemp - 2.*idealT) > 20.):
      Hscore = 0.7
      
    # process wind data
    if wind <= 10.:
      Wscore = 1.0
    elif (wind > 10.) and (wind <= 30.):
      Wscore = 0.9
    elif (wind > 30.) and (wind <= 60.):
      Wscore = 0.7
    elif (wind > 60.) and (wind <= 90.):
      Wscore = 0.4
    elif (wind > 90.):
      Wscore = 0.0
      
    # process condition data
    if condition in condition_dict['excellent']:
      Cscore = 1.0
    elif condition in condition_dict['good']:
      Cscore = 0.8
    elif condition in condition_dict['bad']:
      Cscore = 0.5
    elif condition in condition_dict['terrible']:
      Cscore = 0.1
    else:
      Cscore = 0.6
      
    total_score[i] = Tscore + Hscore + Wscore + Cscore
  return total_score  
      
total_score = compute_score(weather)

# normalize: best score takes 1 point, worst score takes 0 points
norm_score = total_score - total_score.min()
norm_score /= norm_score.max()

weather['weather'] = norm_score

create_table(weather, 'weather')


    
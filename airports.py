# -*- coding: utf-8 -*-

import urllib2
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from sql_functions import *

df = read_table('cities')

# collect airport codes
# first, find the closest airport to each city
# also check: http://www.closestairportto.com/cities/
airports = pd.DataFrame([], columns=['city', 'state_abbr', 'airport'])
for i in range(df.shape[0]):
  city = df.city[i]
  state = df.state_abbr[i]
  if state in airports.state_abbr.values:
    continue
  else:
    print 'downloading data for ', state
    url = 'http://airport.globefeed.com/US_Nearest_Airport.asp?state=' + state
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    table = soup.find('table', {'style':'border-width:1px;border-style:solid;border-color:#E7E7E7'})
    items = []  
    for item in table.findAll('td')[5:]:
      items.append(item.contents[0])
    more_airports = pd.DataFrame([], columns=['city', 'state_abbr', 'airport'])  
    more_airports['city'] = items[::2]
    more_airports['state_abbr'] = state
    more_airports['airport'] = items[1::2]
    airports = pd.concat((airports, more_airports), ignore_index=True)



# second, find airport codes for each airport    
airport_codes = pd.DataFrame([], columns=['airport', 'state_abbr', 'code'])
url = 'http://www.airportcodes.us/us-airports-by-name.htm'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page)
table = soup.find('table', {'class':'c'})
items = []
ind = range(2,14) + range(15,len(table.findAll('tr'))) #avoid advertisement
for row in np.array(table.findAll('tr'))[ind]:
  airport = str(row.findAll('td')[0].contents[0])
  state = str(row.findAll('td')[2].contents[0])
  code = str(row.findAll('td')[3].contents[0])
  print 'downloading data for ', airport
  airport_codes = airport_codes.append({'airport': airport, 'state_abbr': state,
                                        'code': code}, ignore_index=True)



# third, merge cities, states, airports, and airport codes data
airports['airport_code'] = np.nan
for i in range(airports.shape[0]):
  for j in range(airport_codes.shape[0]):
    if (airport_codes.airport[j] in airports.airport[i]) and \
       (airport_codes.state_abbr[j] == airports.state_abbr[i]):
      print 'setting value for ', airports.airport[i]   
      airports.ix[i, 'airport_code'] = airport_codes.code[j]
      break
airports.ix[airports.city == 'New York City', 'city'] = 'New York'
airports.ix[airports.city == 'Chicago', 'airport'] = \
                               "Chicago O'hare International Airport"
airports.ix[airports.city == 'Chicago', 'airport_code'] = 'ORD'                         
airports.ix[airports.airport == 'John F Kennedy International Airport', 
            'airport_code'] = 'JFK'
airports.ix[airports.city == 'Los Angeles', 
                      'airport'] = 'Los Angeles International Airport'         
airports.ix[airports.city == 'Fort Worth', 'airport_code'] = 'DFW'
airports.ix[airports.city == 'Fort Worth', 'airport'] = \
                             'Dallas/Fort Worth International Airport'
airports.ix[airports.city == 'Baltimore', 'airport_code'] = 'BWI'
airports.ix[airports.airport_code == 'BKL', 'airport'] = \
                             'Cleveland Hopkins International Airport'
airports.ix[airports.airport_code == 'BKL', 'airport_code'] = 'CLE'
airports.ix[airports.airport_code == 'OXR', 'airport'] = \
                             'Los Angeles International Airport'
airports.ix[airports.airport_code == 'OXR', 'airport_code'] = 'LAX'
airports.ix[airports.airport_code == 'INT', 'airport'] = \
                             'Piedmont Triad International Airport'
airports.ix[airports.airport_code == 'INT', 'airport_code'] = 'GSO'
airports.ix[airports.airport_code == 'LUK', 'airport'] = \
                  'Cincinnati / Northern Kentucky International Airport'
airports.ix[airports.airport_code == 'LUK', 'airport_code'] = 'CVG'
airports.ix[airports.city == 'Saint Petersburg', 'city'] = 'St. Petersburg'
airports.ix[airports.city == 'Saint Louis', 'city'] = 'St. Louis'
airports.ix[airports.airport == 'Lambert St Louis International Airport', 
            'airport_code'] = 'STL'
airports.ix[airports.airport_code == 'AGC', 'airport'] = \
                             'Pittsburgh International Airport'
airports.ix[airports.airport_code == 'AGC', 'airport_code'] = 'PIT'
airports.ix[airports.airport_code == 'MRI', 'airport'] = \
                             'Anchorage International Airport'
airports.ix[airports.airport_code == 'MRI', 'airport_code'] = 'ANC'
airports.ix[airports.airport_code == 'MKC', 'airport'] = \
                             'Kansas City International Airport'
airports.ix[airports.airport_code == 'MKC', 'airport_code'] = 'MCI'
airports.ix[airports.city == 'Fontana', 'airport'] = \
                             'Los Angeles International Airport'
airports.ix[airports.city == 'Fontana', 'airport_code'] = 'LAX'
airports.ix[airports.airport_code == 'NEW', 'airport'] = \
                             'Louis Armstrong New Orleans International Airport'
airports.ix[airports.airport_code == 'NEW', 'airport_code'] = 'MSY'
airports.ix[airports.airport_code == 'SBD', 'airport'] = \
                             'John Wayne Airport-Orange County Airport'
airports.ix[airports.airport_code == 'SBD', 'airport_code'] = 'SNA'


            
# fourth, find airport codes for every US city that has airport          
airports2 = pd.DataFrame([], columns=['city', 'state_abbr', 'airport', 'code'])
url = 'http://www.airportcodes.us/us-airports-by-state.htm'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page)
table = soup.find('table', {'class':'c'})
items = []
ind = range(2,14) + range(15,len(table.findAll('tr'))) #avoid advertisement
for row in np.array(table.findAll('tr'))[ind]:
  state = str(row.findAll('td')[0].contents[0])
  city = str(row.findAll('td')[1].contents[0])
  code = str(row.findAll('td')[2].contents[0])
  airport = str(row.findAll('td')[3].contents[0])
  print 'downloading data for ', city
  airports2 = airports2.append({'city': city, 'state_abbr': state, 
                                        'airport': airport, 'code': code}, 
                                        ignore_index=True)



# fifth, replace missing values
for i in airports[airports.airport_code.isnull()].index.values:
  for j in range(airports2.shape[0]):
    if (airports.city[i] == airports2.city[j]) and \
       (airports.state_abbr[i] == airports2.state_abbr[j]):
      print 'setting value for ', airports.city[i]   
      airports.ix[i, 'airport_code'] = airports2.code[j]
      break



# sixth manually fill in missing values
missing = []
missing.append({'city': 'Virginia Beach', 'state_abbr': 'VA', 
                'airport': 'Norfolk International Airport',
                'airport_code': 'ORF'})
missing.append({'city': 'Raleigh', 'state_abbr': 'NC', 
                'airport': 'Raleigh-Durham International Airport',
                'airport_code': 'RDU'})
missing.append({'city': 'Arlington', 'state_abbr': 'TX', 
                'airport': 'Dallas/Fort Worth International Airport',
                'airport_code': 'DFW'})
missing.append({'city': 'Aurora', 'state_abbr': 'CO', 
                'airport': 'Denver International Airport',
                'airport_code': 'DEN'})
missing.append({'city': 'Anaheim', 'state_abbr': 'CA', 
                'airport': 'Los Angeles International Airport',
                'airport_code': 'LAX'})
missing.append({'city': 'Riverside', 'state_abbr': 'CA', 
                'airport': 'Los Angeles International Airport',
                'airport_code': 'LAX'})
missing.append({'city': 'Saint Paul', 'state_abbr': 'MN', 
                'airport': 'Minneapolis/St. Paul International Airport',
                'airport_code': 'MSP'})
missing.append({'city': 'Henderson', 'state_abbr': 'NV', 
                'airport': 'Mccarran International Airport',
                'airport_code': 'LAS'})
missing.append({'city': 'Chula Vista', 'state_abbr': 'CA', 
                'airport': 'San Diego International Airport',
                'airport_code': 'SAN'})
missing.append({'city': 'Chandler', 'state_abbr': 'AZ', 
                'airport': 'Phoenix Sky Harbor International Airport',
                'airport_code': 'PHX'})
missing.append({'city': 'St. Petersburg', 'state_abbr': 'FL', 
                'airport': 'Tampa International Airport',
                'airport_code': 'TPA'})
missing.append({'city': 'Durham', 'state_abbr': 'NC', 
                'airport': 'Raleigh-Durham International Airport',
                'airport_code': 'RDU'})
missing.append({'city': 'Gilbert', 'state_abbr': 'AZ', 
                'airport': 'Phoenix Sky Harbor International Airport',
                'airport_code': 'PHX'})
missing.append({'city': 'Glendale', 'state_abbr': 'AZ', 
                'airport': 'Phoenix Sky Harbor International Airport',
                'airport_code': 'PHX'})                
missing.append({'city': 'Hialeah', 'state_abbr': 'FL', 
                'airport': 'Miami International Airport',
                'airport_code': 'MIA'})
missing.append({'city': 'North Las Vegas', 'state_abbr': 'NV', 
                'airport': 'Mccarran International Airport',
                'airport_code': 'LAS'})
missing.append({'city': 'Fremont', 'state_abbr': 'CA', 
                'airport': 'San Jose International Airport',
                'airport_code': 'SJC'})
missing.append({'city': 'Tacoma', 'state_abbr': 'WA', 
                'airport': 'Seattle/Tacoma International Airport',
                'airport_code': 'SEA'})


for i in range(len(missing)):
  ind = airports.ix[airports.city == missing[i]['city']] \
                   [airports.state_abbr == missing[i]['state_abbr']].index.values
  airports.ix[ind, 'airport'] = missing[i]['airport']
  airports.ix[ind, 'airport_code'] = missing[i]['airport_code']
  #airports = airports.append(missing[i], ignore_index=True)

# drop double enetries of the same city
# This is for Mesa, AZ
airports.drop(airports[airports.airport_code == 'IWA'].index.values, inplace=True)             

# for large cities, change code to all airports
airports.ix[(airports.city == 'New York') & (airports.state_abbr == \
            'NY'), ['airport', 'airport_code']] = ('All airports', 'NYC')
airports.ix[(airports.city == 'Chicago') & (airports.state_abbr == \
            'IL'), ['airport', 'airport_code']] = ('All airports', 'CHI')
airports.ix[(airports.city == 'Washington') & (airports.state_abbr == \
            'DC'), ['airport', 'airport_code']] = ('All airports', 'WAS')

# save data in MySQL table
create_table(airports, 'airports')

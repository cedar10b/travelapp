# -*- coding: utf-8 -*-

import urllib2
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from sql_functions import *

df = read_table('cities')

# collect crime data
city = []
for item in df.city.values:
  city.append(str(item).replace(' ', '-'))
city[24] = 'Nashville-Davidson' # Nashville is listed as Nashville-Davidson at city-data.com

state = []
for item in df.state.values: 
  state.append(str(item).replace(' ', '-'))

for i in range(len(city)):
  print 'downloading crime data for ', city[i], state[i]
  url = 'http://www.city-data.com/crime/crime-' + city[i] + '-' + state[i] + '.html'  
  try:  
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    table = soup.find('table', {'class': 'table tabBlue tblsort tblsticky sortable'}) 
    crime_index_row = table.findAll('tr')[9]
    crime_index_values = crime_index_row.findAll('td')[-10:]
    crime_index_values = [float(str(crime_index_values[j])[4:9]) for j in range(len(crime_index_values))]
    crime_index_mean = np.mean(crime_index_values)
    df.ix[i, 'crime'] = crime_index_mean
  except:
    print 'cannot open: ', url
    
# replace missing values with grand average 
df.ix[df.crime.isnull(), 'crime'] = df.crime.mean()

# normalize: lowest crime takes 1 point, highest crime takes 0 points
df['crime'] -= df.crime.min()
df['crime'] /= df.crime.max()
df['safety'] = 1. - df['crime']

create_table(df.ix[:, ['city', 'state_abbr', 'safety']], 'safety')

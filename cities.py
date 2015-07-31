# -*- coding: utf-8 -*-

import re
import urllib2
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from sql_functions import *

df = pd.DataFrame([], columns=['city', 'state', 'population'])

# find the largest cities in the US from wikipedia
url = 'https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page)
table = soup.find('table', {'class': 'wikitable sortable'})
entry = {} 
for row in table.findAll('tr')[1:]:
  city = row.findAll('td')[1].contents[0]
  #state = row.findAll('td')[2].a.attrs['title']
  state = str(row.findAll('td')[2].a)
  state = re.compile('>(.*?)</a>').search(state).group(1)
  population = row.findAll('td')[4].contents[0]
  population = int(population.replace(',', ''))
  city = city.string
  df = df.append({'city': city, 'state': state, 'population': population}, ignore_index=True)
df.ix[df.state.values == "Hawai'i", 'state'] = 'Hawaii'
df.ix[df.city.values == u"Winston\u2013Salem", 'city'] = 'Winston-Salem'



# add state abbreviation
state_abbr = pd.DataFrame([], columns=['state', 'state_abbr'])

url = 'http://www.stateabbreviations.us/'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page)
table = soup.find('table', {'class': 'f'})
for row in table.findAll('tr')[2:]:
  state = str(row.findAll('td')[0].a)
  state = re.compile('>(.*?)</a>').search(state).group(1)
  abbr = row.findAll('td')[2].contents[0]
  state_abbr = state_abbr.append({'state': state, 'state_abbr': abbr}, ignore_index=True)
df = pd.merge(df, state_abbr, on='state', how='left')
df.ix[df.state == 'District of Columbia', 'state_abbr'] = 'DC'


# drop SF Bay Area cities from the list -- you can drive to these cities
bay_area_cities = ['San Jose', 'San Francisco', 'Sacramento', 
                   'Oakland', 'Stockton', 'Fremont', 'Modesto']
for i in range(len(bay_area_cities)):                   
  df.drop(df[df.city == bay_area_cities[i]].index.values, 
              inplace=True)             
df.set_index(pd.Index(np.arange(df.shape[0])), inplace=True)

# normalize population
# scale saturates above 2,500,000 and below 200,000
# the log is taken and it is normalized from 0 to 1.
trunc_pop = np.where(df.population > 2500000, 2500000, df.population)
trunc_pop = np.where(df.population < 200000, 200000, trunc_pop)
trunc_pop = np.log(trunc_pop)
trunc_pop -= trunc_pop.min()
trunc_pop /= trunc_pop.max()

df['norm_popul'] = trunc_pop

create_table(df, 'cities')

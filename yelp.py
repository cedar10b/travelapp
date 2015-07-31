# -*- coding: utf-8 -*-

import requests
import urllib2
import numpy as np
import pandas as pd
from requests_oauthlib import OAuth1
from sql_functions import *

df = read_table('cities')

# collect restaurants and bars data
HOST = 'api.yelp.com'
PATH = '/v2/search/'
url = 'http://{0}{1}?'.format(HOST, urllib2.quote(PATH.encode('utf8')))

CONSUMER_KEY = '***'
CONSUMER_SECRET = '***'
TOKEN = '***'
TOKEN_SECRET = '***'
auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, TOKEN, TOKEN_SECRET)

bars = []
for i in range(df.shape[0]):
  location = df.city[i] + ', ' + df.state_abbr[i]
  print location
  params = {'term': "bars", 'location': location, 'limit': 20, 'sort': 2}
  req = requests.get(url, auth=auth, params=params)
  bars.append(req.json())
for i in range(df.shape[0]):
  mean_bar_rating = np.mean( [bars[i]['businesses'][j]['rating'] \
                              for j in range(len(bars[0]['businesses']))] )
  df.ix[i, 'bars'] = mean_bar_rating

restaurants = []
for i in range(df.shape[0]):
  location = df.city[i] + ', ' + df.state_abbr[i]
  print location
  params = {'term': "restaurants", 'location': location, 'limit': 20, 'sort': 2}
  req = requests.get(url, auth=auth, params=params)
  restaurants.append(req.json())
for i in range(df.shape[0]):
  mean_rest_rating = np.mean( [restaurants[i]['businesses'][j]['rating'] \
                              for j in range(len(restaurants[0]['businesses']))] )
  df.ix[i, 'restaurants'] = mean_rest_rating

# normalize: best score takes 1 point, worst score takes 0 points
df['bars'] -= df.bars.min()
df['restaurants'] -= df.restaurants.min()
df['bars'] /= df.bars.max()
df['restaurants'] /= df.restaurants.max()

create_table(df.ix[:, ['city', 'state_abbr', 'bars', 'restaurants']], 'yelp')


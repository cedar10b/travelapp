# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sql_functions import *

# number of cities to include in search
N = 100

# number of cities to include in results
top = 10

# read and combine dataframes into one dataframe
cities = read_table('cities')
airfare = read_table('airfare')
weather = read_table('weather')
yelp = read_table('yelp')
safety = read_table('safety')

df = pd.merge(cities.ix[0:N-1, ['city', 'state_abbr', 'norm_popul']], 
              safety, on=['city', 'state_abbr'], how='left')
df = pd.merge(df, weather.ix[:, ['city', 'state_abbr', 'weather',
                                 'mintemp', 'maxtemp', 'condition']],
                                 on=['city', 'state_abbr'], how='left')
df = pd.merge(df, yelp.ix[:, ['city', 'state_abbr', 'bars', 'restaurants']],
              on=['city', 'state_abbr'], how='left')
df = pd.merge(df, airfare.ix[:, ['city', 'state_abbr', 'airfare']],
              on=['city', 'state_abbr'], how='left')
              
create_table(df, 'main')


def rank(df, norm_popul=5, safety=5, bars=5, weather=5, airfare=500):
  
  # compute a weighted average according to user's input 
  #and normalize from 0 to 10
  scores = norm_popul*df.norm_popul + safety*df.safety + \
           bars*df.bars + weather*df.weather
  scores -= scores.min()
  scores /= 0.1*scores.max() #normalize from 0 to 10
  scores = np.where(df.airfare <= airfare, np.round(scores, 2), 0.0)

  
  # visualize output  
  order = np.argsort(scores)[::-1]
  final_scores = scores[order][0:top][::-1]
  city = np.array([str(df.city[order[i]]) for i in range(top)])[::-1]
  state = np.array([str(df.state_abbr[order[i]]) for i in range(top)])[::-1]
  best = np.array([city[i] + ', ' + state[i] for i in range(top)])

              
  sns.set_style("whitegrid")
  plt.barh(np.arange(top), final_scores, align='center')
  plt.ylim((-1, top))
  plt.xlim(np.floor(final_scores[0]), np.ceil(final_scores[-1]))
  plt.yticks(np.arange(top), best)
  plt.xlabel('Score', fontsize=18)
  plt.title('Top ten cities', fontsize=18)
  plt.tick_params(labelsize=18)
  #fig = plt.gcf()
  #fig.set_size_inches(6,8)
  #fig.savefig('fig2.png', bbox_inches='tight')
  plt.show()
  
  print 'Best match: ', best[-1]
  print 'Cost of airfare: ', df.airfare[order[0]]
  print 'Temperature from ', df.mintemp[order[0]], 'to ', df.maxtemp[order[0]], ' F'
  print 'Weather forecast: ', df.condition[order[0]]



__author__ = 'Arif'

# Disclaimer.
# this script is still under (very early) development.
# some code are taken from book 'Mining The Social Web, 2nd Edition' by Matthew A. Russel
#

import twitter
import json
from urllib.parse import unquote
from collections import Counter
import csv
from os import listdir
from os.path import isfile, join
import numpy as np
import matplotlib.pyplot as plt

# Twitter API data
CONSUMER_KEY=''
CONSUMER_SECRET=''

ACCESS_TOKEN=''
ACCESS_TOKEN_SECRET=''

#some parameters
count = 100
q = '#jokowi'

# do authentication
auth = twitter.oauth.OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
twitter_api = twitter.Twitter(auth=auth)

search_results = twitter_api.search.tweets(q=q,count=count)
statuses = search_results['statuses']

#iterate through 5 more batches of results by following the cursor
for _ in range(5):
    #print("Length of statuses: ", len(statuses))
    try:
        #example for next_results: ?max_id=595316981110157311&q=%23jokowi&count=1&include_entities=1
        next_results = search_results['search_metadata']['next_results']
    except KeyError as e:
        break

    #create a dictionary from next_results
    kwargs = dict([kv.split('=') for kv in unquote(next_results[1:]).split("&")])

    search_results = twitter_api.search.tweets(**kwargs)
    statuses += search_results['statuses']

status_texts = [status['text']
                 for status in statuses]
screen_names = [user_mention['screen_name']
                 for status in statuses
                 for user_mention in status['entities']['user_mentions']]
hashtags = [hashtag['text']
             for status in statuses
             for hashtag in status['entities']['hashtags']]

#compute a collection of all words from all tweets
words = [w for t in status_texts for w in t.split()]

counter = 0
whole_data = [words, screen_names, hashtags]
whole_data_string = ["words", "screen_names", "hashtags"] #dirty solution

dir = 'csv/'
for item in whole_data:
   #for csv filename index
    c = Counter(item)
    data = dict(c.most_common()[:100])
    filename = dir + 'output_' + whole_data_string[counter] + '.csv'

    with open(filename,'w',encoding='utf-8', newline='') as csvfile:
        print('writing ', filename,'...')
        writer = csv.writer(csvfile, delimiter='|')
        for key,value in data.items():
            writer.writerow([key.encode('ascii','replace'),value])
        print('writing finished.')
    counter += 1

#--------------------------
#plot
#--------------------------
# 1. open the csv file
file_list = [f for f in listdir(dir) if isfile(join(dir,f))]
print(file_list)

counter = 0
for filename in file_list:
    #variable, value = np.loadtxt(dir + filename, delimiter=',', unpack=True, dtype=None)
    variable = np.genfromtxt(dir+filename, dtype=None, delimiter='|',usecols=[0])
    value = np.genfromtxt(dir+filename, dtype=None, delimiter='|', usecols=[1])

    ax = plt.subplot(len(file_list),1,counter+1)
    x_axis = np.arange(len(variable))
    ax.bar(x_axis, value, color="b")
    plt.xticks(x_axis, variable)
    plt.ylabel(whole_data_string[counter])
    
    print(filename)
    counter += 1

# 2. create bar chart
plt.show()
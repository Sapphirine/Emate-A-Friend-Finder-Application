import time
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import os
import io
import pandas as pd
import numpy as ny
import json


#Variables that contains the user credentials to access Twitter API 
access_token = "698964662986088448-0Ep82VpULt72l14p9t93FkIPHdVhlL3"
access_token_secret = "8BVqXYht2bLaREW7hZpMugbUz8cQLK5MYP26hmPH6gkhY"
consumer_key =  "sQyaBlDjkJSnvucR0KFf0jw9V"
consumer_secret =  "oyuTfNQyl8YABpPJBDYzoSEGeoNTEUbZwydrH1PyNPfdWgrbtt"

START_TIME = time.time() #grabs the system time
TIME_LIMIT = 4000
keyword_list = ['twitter'] #track list
east_coast = [-128.76,23.83,-60.47,51.37]

#Listener Class Override
class TwitterListener(StreamListener):
 
  def __init__(self, start_time, time_limit=60):
 
    self.time = start_time
    self.limit = time_limit
    self.tweet_data = []

  def on_data(self, data):

    saveFile = io.open('raw_tweets.json', 'a', encoding='utf-8')

    while (time.time() - self.time) < self.limit:
      try:
        self.tweet_data.append(data)
        return True

      except BaseException, e:
        print 'failed ondata, ', str(e)
        time.sleep(5)
        pass

    saveFile = io.open('raw_tweets.json', 'w', encoding='utf-8')
    saveFile.write(u'[\n')
    saveFile.write(','.join(self.tweet_data))
    saveFile.write(u'\n]')
    saveFile.close()
    return False

  def on_error(self, status):
    
    print statuses

class DataFetcher():
  def __init__(self):
    self.id_dict = {}

  def fetch_data(self):
    print 'Fetching tweet data, please wait...'
    auth = OAuthHandler(consumer_key, consumer_secret) #OAuth object
    auth.set_access_token(access_token, access_token_secret)
    twitterStream = Stream(auth, TwitterListener(START_TIME, TIME_LIMIT)) #initialize Stream object with a time out limit
    #twitterStream.filter(track=keyword_list, languages = ['en'])  #call the filter method to run the Stream Object
    twitterStream.filter(locations=east_coast, languages=['en'])

  def parse_data(self):
    json_data = open('raw_tweets.json')
    python_obj = json.load(json_data)

    for obj in python_obj:
      if 'id' in obj.keys() and obj['coordinates'] != None:
        self.id_dict[obj['id']] = {'text': obj['text'], 'coordinates': obj['coordinates']}
      else:
        continue

  def get_dict(self):
    return self.id_dict

  def run_all(self):
    self.fetch_data()
    self.parse_data()
    return self.get_dict()

if __name__ == '__main__':
  datafetcher = DataFetcher()
  d = datafetcher.run_all()
  print d
  print len(d)
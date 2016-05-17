import sys
from math import log10, sqrt
from DataFetcher import DataFetcher
from collections import defaultdict
import numpy as np
import operator

class TweetsProcessor():
  def __init__(self, tweets_dict, normalize=True):
    self.tweets_dict = tweets_dict
    self.word_dict = {}
    self.word_to_vec_idx = {}
    self.id_to_vec_dict = {}
    self.df = defaultdict(int)
    self.normalize = normalize

  def clear(self):
    self.word_dict = {}
    self.word_to_vec_idx = {}
    self.id_to_vec_dict = {}
    self.df = defaultdict(int)

  def prepare(self):
    print 'Processing tweets, please wait...'
    # Step 1, generate mappings from each word to its corresponding location in feature vector,
    # which is stored in self.word_to_vec_idx
    word_count = 0
    for tweet_id in self.tweets_dict.keys():
      tweet = self.tweets_dict[tweet_id]['text']
      # get each word of the tweet
      tokens = self.word_list_from_tweet(tweet)

      for word in tokens:
        if word in self.word_dict.keys():
          continue
        else:
          self.word_dict[word] = True
          self.word_to_vec_idx[word] = word_count
          word_count += 1

    # Step 2, calculate df (document frequency) for each word in the dictionary.
    for tweet_id in self.tweets_dict.keys():
      tweet = self.tweets_dict[tweet_id]['text']
      tokens = self.word_list_from_tweet(tweet)

      for word in self.word_dict.keys():
        if word in tokens:
          self.df[word] += 1
        else:
          continue

    # Step 3, generate feature vector (tf-idf vector) for each tweet and store them in 
    # self.id_to_vec_dict
    for tweet_id in self.tweets_dict.keys():
      tweet = self.tweets_dict[tweet_id]['text']
      lat = self.tweets_dict[tweet_id]['coordinates']['coordinates'][0]
      lng = self.tweets_dict[tweet_id]['coordinates']['coordinates'][1]

      feature_vector = self.convert_tweet_to_vec(tweet, lat, lng)
      self.id_to_vec_dict[tweet_id] = feature_vector

  def convert_tweet_to_vec(self, tweet, lat, lng):
    tokens = self.word_list_from_tweet(tweet)
    total_word_count = len(self.word_dict)

    # initialize the vector with zeros
    vec = np.zeros(total_word_count + 2)

    # calculate tf
    for word in tokens:
      if word in self.word_dict.keys():
        idx = self.word_to_vec_idx[word]
        vec[idx] += 1.
        if self.normalize:
          vec[idx] /= float(len(tokens))

    # mutiply by idf
    for word in tokens:
      if word in self.word_dict.keys():
        idx = self.word_to_vec_idx[word]
        df = self.df[word]
        vec[idx] *= 1 + (log10(float(len(tokens)) / df))

    # store latitude and longitude in feature vector
    vec[-2] = lat
    vec[-1] = lng
    return vec

  # this is the method that will be called by outsider: given a tweet as an input, returns
  # a list of n most similar tweets. 
  def get_similar_tweets(self, tweet, lat, lng, n=5):
    if n > len(self.tweets_dict):
      n = len(self.tweets_dict)

    vec_input = self.convert_tweet_to_vec(tweet, lat, lng)
    all_vecs = self.get_all_feature_vectors()

    score_to_id = {}
    scores = []

    # calcualte all similaritis between input tweet and all fetched tweets
    for tweet_id, vec in all_vecs.iteritems():
      score = self.calculate_similarity(vec, vec_input)
      score_to_id[tweet_id] = score

    # sort and pick top n
    score_to_id = sorted(score_to_id.items(), key=operator.itemgetter(1), reverse=True)[:n]

    most_similar_tweets = []
    for (tweet_id, score) in score_to_id:
      if score > 0.0:
        tweet = self.tweets_dict[tweet_id]['text']
        coordinates = self.tweets_dict[tweet_id]['coordinates']
        most_similar_tweets.append([tweet, tweet_id, score, coordinates])

    return most_similar_tweets

  def calculate_similarity(self, t_a, t_b):
    t_a_p = t_a[:-2]
    t_b_p = t_b[:-2]

    # latitudes
    lat_a = t_a[-2]
    lat_b = t_b[-2]

    # longitudes
    lng_a = t_a[-1]
    lng_b = t_b[-1]

    # cosine similarity + 5 / (longitude-based distance between two locations)
    if np.linalg.norm(t_a_p) == 0. or np.linalg.norm(t_b_p) == 0.:
      return 0.
    else:
      return np.dot(t_a_p, t_b_p) / (np.linalg.norm(t_a_p) * np.linalg.norm(t_b_p)) + 5. / (sqrt((lat_a - lat_b) ** 2 + (lng_a - lng_b) ** 2) + 5.)

  def get_all_feature_vectors(self):
    return self.id_to_vec_dict

  def word_list_from_tweet(self, tweet):
    return tweet.lower().strip().split()

# for testing
if __name__ == '__main__':

  data_fetcher = DataFetcher()
  tweets = data_fetcher.run_all()
  print len(tweets)
  tp = TweetsProcessor(tweets)
  tp.prepare()

  print 'Start testing mode, input a fake tweet, for example:'
  print 'hello what is your name I am fine thank you USA america I am a happy girl, will return'
  similar_tweets = tp.get_similar_tweets('hello what is your name I am fine thank you USA america I am a happy girl')
  print '============================'
  print 'Similar Ones:'
  for tweet in similar_tweets:
    print tweet
    print '----------------------------'
  print 'Try it yourself!'
  print ''
  print ''
  while True:
    print 'Please enter your tweet:'
    tweet = raw_input()
    similar_tweets = tp.get_similar_tweets(tweet)
    print '============================'
    print 'Similar Ones:'
    for tweet in similar_tweets:
      print tweet
      print '----------------------------'
      print ''
      print ''
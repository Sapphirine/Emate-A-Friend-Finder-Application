"""
This script runs the TwitterMapProj application using a development server.
"""

from os import environ, system
from datetime import datetime
from flask import render_template, jsonify, Flask
from pyes import *

from DataFetcher import DataFetcher
from TweetsProcessor import TweetsProcessor

application = app = Flask(__name__)
tweetsProcessor = None

def init_tweetsprocessor():
    global tweetsProcessor
    dataFetcher = DataFetcher()
    #tweets_dict = dataFetcher.run_all()
    dataFetcher.parse_data()
    tweets_dict = dataFetcher.get_dict()
    tweetsProcessor = TweetsProcessor(tweets_dict)
    tweetsProcessor.prepare()

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""

    return render_template(
        'mainTwitterMap.html',
        title='Main Twitter Map Page',
        year=datetime.now().year,
    )

@app.route('/getTwits/<keywords>')
def get_tweets(keywords):
    global tweetsProcessor
    tokens = keywords.split()
    words = ''
    for t in tokens[:-2]:
        words += t + ' '
    lat = float(tokens[-2])
    lng = float(tokens[-1])

    words = words.encode('utf-8')
    data = []

    results = tweetsProcessor.get_similar_tweets(words, lat, lng)

    for line in results:
        data.append({'longitude': line[3]['coordinates'][0], 'latitude': line[3]['coordinates'][1], 'text': line[0]})
    return jsonify({'data':data})

@app.route('/refetch')
def refetch():
    init_tweetsprocessor()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    global tweetsProcessor
    if tweetsProcessor is None:
      init_tweetsprocessor()
    app.run(debug=True, host='0.0.0.0')
    #app.run()
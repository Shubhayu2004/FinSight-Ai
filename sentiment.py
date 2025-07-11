import pandas as pd
import tweepy
import preprocessor as p
import re
from textblob import TextBlob
import constants as ct
from Tweet import Tweet
import matplotlib.pyplot as plt

def retrieving_tweets_polarity(symbol):
    stock_ticker_map = pd.read_csv('Yahoo-Finance-Ticker-Symbols.csv')
    stock_full_form = stock_ticker_map[stock_ticker_map['Ticker'] == symbol]
    symbol = stock_full_form['Name'].to_list()[0][0:12]
    auth = tweepy.OAuthHandler(ct.consumer_key, ct.consumer_secret)
    auth.set_access_token(ct.access_token, ct.access_token_secret)
    user = tweepy.API(auth)
    tweets = tweepy.Cursor(user.search_tweets, q=symbol, tweet_mode='extended', lang='en', exclude_replies=True).items(ct.num_of_tweets)
    tweet_list = []
    global_polarity = 0
    tw_list = []
    pos = 0
    neg = 1
    for tweet in tweets:
        count = 20
        tw2 = tweet.full_text
        tw = tweet.full_text
        tw = p.clean(tw)
        tw = re.sub('&amp;', '&', tw)
        tw = re.sub(':', '', tw)
        tw = tw.encode('ascii', 'ignore').decode('ascii')
        blob = TextBlob(tw)
        polarity = 0
        for sentence in blob.sentences:
            polarity += sentence.sentiment.polarity
            if polarity > 0:
                pos = pos + 1
            if polarity < 0:
                neg = neg + 1
            global_polarity += sentence.sentiment.polarity
        if count > 0:
            tw_list.append(tw2)
        tweet_list.append(Tweet(tw, polarity))
        count = count - 1
    if len(tweet_list) != 0:
        global_polarity = global_polarity / len(tweet_list)
    neutral = ct.num_of_tweets - pos - neg
    if neutral < 0:
        neg = neg + neutral
        neutral = 20
    labels = ['Positive', 'Negative', 'Neutral']
    sizes = [pos, neg, neutral]
    explode = (0, 0, 0)
    fig = plt.figure(figsize=(7.2, 4.8), dpi=65)
    fig1, ax1 = plt.subplots(figsize=(7.2, 4.8), dpi=65)
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    plt.tight_layout()
    plt.savefig('static/SA.png')
    plt.close(fig)
    if global_polarity > 0:
        tw_pol = "Overall Positive"
    else:
        tw_pol = "Overall Negative"
    return global_polarity, tw_list, tw_pol, pos, neg, neutral

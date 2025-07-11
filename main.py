# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 14:36:49 2019

@author: Kaushik
"""
#**************** IMPORT PACKAGES ********************
from flask import Flask, render_template, request, flash, redirect, url_for
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import math, random
from datetime import datetime
import datetime as dt
import yfinance as yf
import tweepy
import preprocessor as p
import re
from sklearn.linear_model import LinearRegression
from textblob import TextBlob
import constants as ct
from Tweet import Tweet
import nltk
nltk.download('punkt')
import csv

# Ignore Warnings
import warnings
warnings.filterwarnings("ignore")
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

#***************** FLASK *****************************
app = Flask(__name__)

#To control caching so as to save and retrieve plot figs on client side
@app.after_request
def add_header(response):
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response

# Helper function to read tickers from CSV
def get_tickers():
    tickers = []
    try:
        with open('Data/Yahoo-Finance-Ticker-Symbols.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                tickers.append({'symbol': row['Ticker'], 'name': row['Name']})
    except Exception as e:
        print(f"Error reading tickers: {e}")
    return tickers

@app.route('/')
def index():
    tickers = get_tickers()
    return render_template('index.html', tickers=tickers, results=None)

@app.route('/insertintotable', methods=['POST'])
def insertintotable():
    nm = request.form['nm']

    #**************** FUNCTIONS TO FETCH DATA ***************************
    def get_historical(quote):
        end = datetime.now()
        start = datetime(end.year-2,end.month,end.day)
        data = yf.download(quote, start=start, end=end)
        df = pd.DataFrame(data=data)
        df.to_csv(''+quote+'.csv')
        if(df.empty):
            ts = TimeSeries(key='N6A6QT6IBFJOPJ70',output_format='pandas')
            data, meta_data = ts.get_daily_adjusted(symbol='NSE:'+quote, outputsize='full')
            #Format df
            #Last 2 yrs rows => 502, in ascending order => ::-1
            data=data.head(503).iloc[::-1]
            data=data.reset_index()
            #Keep Required cols only
            df=pd.DataFrame()
            df['Date']=data['date']
            df['Open']=data['1. open']
            df['High']=data['2. high']
            df['Low']=data['3. low']
            df['Close']=data['4. close']
            df['Adj Close']=data['5. adjusted close']
            df['Volume']=data['6. volume']
            df.to_csv(''+quote+'.csv',index=False)
        return

    #******************** ARIMA SECTION ********************
        
        


    #************* LSTM SECTION **********************

    #***************** LINEAR REGRESSION SECTION ******************       

    #**************** SENTIMENT ANALYSIS **************************







    #**************GET DATA ***************************************
    quote=nm
    #Try-except to check if valid stock symbol
    try:
        get_historical(quote)
    except:
        tickers = get_tickers()
        return render_template('index.html', tickers=tickers, not_found=True, results=None)
    else:
        df = pd.read_csv(''+quote+'.csv')
        today_stock=df.iloc[-1:]
        df = df.dropna()
        code_list=[]
        for i in range(0,len(df)):
            code_list.append(quote)
        df2=pd.DataFrame(code_list,columns=['Code'])
        df2 = pd.concat([df2, df], axis=1)
        df=df2
        arima_pred, error_arima=ARIMA_ALGO(df, quote)
        lstm_pred, error_lstm=LSTM_ALGO(df, quote)
        df, lr_pred, forecast_set,mean,error_lr=LIN_REG_ALGO(df, quote)
        # Twitter Lookup is no longer free in Twitter's v2 API
        polarity, tw_list, tw_pol, pos, neg, neutral = 0, [], "Can't fetch tweets, Twitter Lookup is no longer free in API v2.", 0, 0, 0
        # If you have Twitter API access, uncomment the next line:
        # polarity, tw_list, tw_pol, pos, neg, neutral = retrieving_tweets_polarity(quote)
        idea, decision=recommending(df, polarity, today_stock, mean, quote)
        today_stock=today_stock.round(2)
        tickers = get_tickers()
        results = {
            'quote': quote,
            'arima_pred': round(arima_pred,2),
            'lstm_pred': round(lstm_pred,2),
            'lr_pred': round(lr_pred,2),
            'open_s': today_stock['Open'].to_string(index=False),
            'close_s': today_stock['Close'].to_string(index=False),
            'adj_close': today_stock['Adj Close'].to_string(index=False),
            'tw_list': tw_list,
            'tw_pol': tw_pol,
            'idea': idea,
            'decision': decision,
            'high_s': today_stock['High'].to_string(index=False),
            'low_s': today_stock['Low'].to_string(index=False),
            'vol': today_stock['Volume'].to_string(index=False),
            'forecast_set': forecast_set,
            'error_lr': round(error_lr,2),
            'error_lstm': round(error_lstm,2),
            'error_arima': round(error_arima,2)
        }
        return render_template('index.html', tickers=tickers, results=results, not_found=False)
if __name__ == '__main__':
   app.run()
   


















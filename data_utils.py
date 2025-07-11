import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from datetime import datetime
import csv

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

def get_historical(quote):
    end = datetime.now()
    start = datetime(end.year-2,end.month,end.day)
    data = yf.download(quote, start=start, end=end)
    df = pd.DataFrame(data=data)
    df.to_csv(''+quote+'.csv')
    if(df.empty):
        ts = TimeSeries(key='N6A6QT6IBFJOPJ70',output_format='pandas')
        data, meta_data = ts.get_daily_adjusted(symbol='NSE:'+quote, outputsize='full')
        data=data.head(503).iloc[::-1]
        data=data.reset_index()
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
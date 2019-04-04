import boto3
from time import sleep
from collections import OrderedDict
import requests
import json
import time

s3 = boto3.resource('s3')
bucket = s3.Bucket('lypang-investment-research')

API_KEY = open('token.txt').read().strip()
BASE_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&apikey=%s&datatype=csv&outputsize=full'

def fetch_prices(event, context):
  start_time = time.time()
  
  tsx_tickers = bucket.Object('tsx_tickers.txt').get()['Body'].read().split('\n')
  tsxv_tickers = bucket.Object('tsxv_tickers.txt').get()['Body'].read().split('\n')
  raw_tickers = tsx_tickers + tsxv_tickers
  
  tickers = OrderedDict()
  for ticker in raw_tickers:
    if '.' in ticker:
      new_ticker = ticker.split('.')[0]
      tickers[new_ticker] = True
    tickers[ticker] = True
  tickers = tickers.keys()
  
  try:
    last_ticker = bucket.Object('last_ticker.txt').get()['Body'].read()
    flag = False
  except:
    last_ticker = None
    flag = True
    
  try:
    errors = bucket.Object('errors.txt').get()['Body'].read().split('\n')
  except:
    errors = []
   
  for ticker in tickers:
    if flag:
      r = requests.get(BASE_URL % (ticker, API_KEY))
      output = r.text
      try:
        json.loads(r.text)
        errors.append(ticker)
        print('Failed for ticker %s' % ticker)
        continue
      except:
        bucket.Object('prices/%s.csv' % ticker).put(Body=r.text)
        bucket.Object('last_ticker.txt').put(Body=ticker)
        print('Succeeded for ticker %s' % ticker)
      finally:
        time.sleep(10)
    elif ticker == last_ticker:
      flag = True
    if time.time() - start_time > 300:
      break
  
  bucket.Object('errors.txt').put(Body='\n'.join(errors))
#REST API
from flask import Flask
from pandas.io.json import json_normalize
from flask import request
from flask_restful import Resource, Api
import json
import requests
import pandas as pd
import pprint
import datetime
import numpy as np

app = Flask(__name__)


#最新のレートを取得
@app.route('/GMO/ticker', methods=['GET'])
def index():

 alt_coin = request.args.get('alt_coin', '') 
 params = {'symbol': alt_coin}
 response = requests.get('https://api.coin.z.com/public/v1/ticker', params=params)
#JSONをパースして買いレートを取得
 json_obj = response.json()
 result = json_obj['data'][0]['ask']
 return result

@app.route('/GMO/dev', methods=['GET'])
def getDeviation():
 alt_coin =request.args.get('alt_coin', '')
 #現在データ取得
 params = {'symbol': alt_coin}
 response1 = requests.get('https://api.coin.z.com/public/v1/ticker', params=params)
 #JSONをパースして買いレートを取得
 json_obj = response1.json()
 result1 = json_obj['data'][0]['ask']

 #現在時刻取得
 now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))) # 日本時刻
 today = now.strftime('%Y%m%d')
 thisYear = now.strftime('%Y')
 now = now + datetime.timedelta(days=-1)
 yesterday = now.strftime('%Y%m%d')
 #KLine情報の取得 （当日）
 params = {'symbol': alt_coin, 'interval': '1min', 'date':today}
 response = requests.get('https://api.coin.z.com/public/v1/klines', params=params)
 #JSONからDataFrame作成
 json_obj = response.json()
 json_obj = json_obj['data']
 hist_data = json_normalize(data=json_obj)
 #昨日データ
 params = {'symbol': alt_coin, 'interval': '1min', 'date':yesterday}
 response = requests.get('https://api.coin.z.com/public/v1/klines', params=params)
 #JSONからDataFrame作成
 json_obj = response.json()
 json_obj = json_obj['data']
 hist_data = hist_data.append(json_normalize(data=json_obj))
 #UnixTimeStamp変換
 hist_data['openTime'] = pd.to_datetime(hist_data['openTime'], unit='ms')
 hist_data = hist_data[['openTime', 'close']]

 hist_data = hist_data.assign(
     alt_coin = alt_coin
 )
 hist_data = hist_data.sort_values('openTime')

 #Indexで最新20件を取得
 latest_df = hist_data.copy()
 sigma =2
 duration = 10 #XX分ごとの移動平均と標準偏差を取得

 #移動平均と標準偏差
 #10分前までの偏差
 latest_df["10_SMA"] = latest_df["close"].rolling(window=10).mean() #移動平均
 latest_df["10_std"] = latest_df["close"].rolling(window=10).std() #標準偏差
 latest_df["10_limit"] = latest_df["10_SMA"]-sigma*latest_df["10_std"]
 latest_df["30_SMA"] = latest_df["close"].rolling(window=30).mean() #移動平均
 latest_df["30_std"] = latest_df["close"].rolling(window=30).std() #標準偏差
 latest_df["30_limit"] = latest_df["30_SMA"]-sigma*latest_df["30_std"]
 latest_df["60_SMA"] = latest_df["close"].rolling(window=60).mean() #移動平均
 latest_df["60_std"] = latest_df["close"].rolling(window=60).std() #標準偏差
 latest_df["60_limit"] = latest_df["60_SMA"]-sigma*latest_df["60_std"]
 latest_df["1day_SMA"] = latest_df["close"].rolling(window=1440).mean() #移動平均
 latest_df["1day_std"] = latest_df["close"].rolling(window=1440).std() #標準偏差
 latest_df["1day_limit"] = latest_df["1day_SMA"]-sigma*latest_df["1day_std"]
 #最新行を取得
 max_idx = (len(latest_df) - 1)
 latest_df = latest_df.iloc[max_idx]
 #小数点、第2桁まで表示
 ten_min_pred = latest_df['10_limit']
 ten_min_pred = '{:.2f}'.format(ten_min_pred)
 thirty_min_pred = latest_df['30_limit']
 thirty_min_pred = '{:.2f}'.format(thirty_min_pred)
 hour_pred = latest_df['60_limit']
 hour_pred = '{:.2f}'.format(hour_pred)
 day_pred = latest_df['1day_limit']
 day_pred = '{:.2f}'.format(day_pred)
 result2 = ten_min_pred + "," + thirty_min_pred + "," + hour_pred + "," +  day_pred
 result1 = '{:.2f}'.format(float(result1))
 result = result1 + '/' + result2
 return result

 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080', debug=True)

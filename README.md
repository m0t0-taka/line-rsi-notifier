## 機能概要

指定したティッカーシンボルの RSI が 25 を下回ったら LINE で通知する

## Python 環境

`pyenv lodal 3.9.9`

## LINE の設定

[LINE Developers](https://developers.line.biz/console/)

- プロバイダーの作成
- チャンネルの作成。「Messaging API」を選択
- QR コードよりチャンネルを友達追加
  ![QR コード](https://qr-official.line.me/sid/L/297zwrzb.png)

## install package

`pip install pandas yfinance ta line-bot-sdk python-dotenv schedule`

## local 環境での実行

`python main.py`

## GCP デプロイ

GCP でプロジェクトを作成したら以下 3 つの API を有効にする

- Cloud Functions API
- Google Cloud Build API
- Cloud Scheduler API

- 前提として [Google Cloud SDK がインストールされている](https://cloud.google.com/sdk/docs/install?hl=ja)

python のサポートバージョンは最新で 3.9

`gcloud init`

デプロイコマンド

`gcloud functions deploy rsi_notifier --runtime python39 --trigger-http --allow-unauthenticated --project line-notify-rsi`

- gcloud functions deploy: Google Cloud Functions に関数をデプロイするための gcloud コマンド
- rsi_notifier: デプロイする関数の名前。これは function.py で定義した関数名と一致している必要あり
- --runtime python39: 関数が実行されるランタイムを指定。ここでは、Python 3.9 を使用
- --trigger-http: 関数のトリガーを HTTP に設定。これにより、関数は HTTP リクエストで呼び出すことができる。
- --allow-unauthenticated: 関数を認証なしで呼び出すことができるように設定。これは、関数をパブリックに公開することを意味する。リスクがある場合はこのオプションを使用しない。
- --project line-notify-rsi: 関数をデプロイする Google Cloud プロジェクトの ID を指定する。
- --env-vars-file env.yaml: env.yaml ファイルに定義した環境変数を設定する

Google Cloud Functions のログを確認する方法

`gcloud functions logs read rsi_notifier --project line-notify-rsi`

## 最終的に行ったデプロイまとめ

- CLI でうまくいかなかったためすべて GUI でデプロイ
- Cloud Functions の設定
  - トリガータイプ HTTP ではなく Cloud Pub/Sub を選択する
    Cloud Scheduler を使用して Cloud Function を定期的に実行するためにはこちらを選択する
  - 最終的に記述したコードは以下 2 ファイル
- Cloud Scheduler の設定

main.py

```py
import os
import yfinance as yf
from ta.momentum import RSIIndicator
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 環境変数を読み込む
LINE_CHANNEL_ACCESS_TOKEN = LINE_CHANNEL_ACCESS_TOKEN
LINE_USER_ID = LINE_USER_ID

# LINE APIを初期化する
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def get_stock_data(ticker_symbol, period="60d", interval="1d"):
    # Yahoo Financeから株価データを取得する
    stock_data = yf.download(ticker_symbol, period=period, interval=interval)
    return stock_data

def calculate_rsi(data, window=14):
    # RSIを計算する
    rsi_indicator = RSIIndicator(close=data["Close"], window=window)
    rsi = rsi_indicator.rsi()
    return rsi

def send_line_notification(message):
    # LINEに通知を送る
    line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=message))
    print("LINE message sent:", message)

def check_rsi_and_notify(ticker_symbols):
    for ticker_symbol in ticker_symbols:
        # 各ティッカーシンボルの株価データを取得
        data = get_stock_data(ticker_symbol)
        print(ticker_symbol)
        print("data", data)
        # RSIを計算
        rsi = calculate_rsi(data)
        print("rsi", rsi)

        # 最新のRSIを取得
        last_rsi = rsi.iloc[-1]
        print("last_rsi", last_rsi)

        # 最新のRSIが20未満の場合、LINEで通知を送る
        if last_rsi < 25:
            message = f"{ticker_symbol}の日足RSIが25を切りました。\n現在のRSI: {last_rsi:.2f}\nチャンス！"
            send_line_notification(message)

def rsi_notifier(event, context):
    # 監視するティッカーシンボルのリスト
    ticker_symbols = ["VOO", "VT", "VWO", "SPYD", "HDV", "VYM", "VIG", "SDY"]

    # RSIをチェックし、通知が必要な場合は送信する
    check_rsi_and_notify(ticker_symbols)
```

requirements.txt

```
yfinance
ta
line-bot-sdk
```

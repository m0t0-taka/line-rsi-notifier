import os
import yfinance as yf
from ta.momentum import RSIIndicator
from linebot import LineBotApi
from linebot.models import TextSendMessage
import schedule
import time
from dotenv import load_dotenv
load_dotenv()

# 環境変数を読み込む
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
LINE_USER_ID = os.environ['LINE_USER_ID']

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
    all_last_rsi_over_25 = True

    for ticker_symbol in ticker_symbols:
        # 各ティッカーシンボルの株価データを取得
        data = get_stock_data(ticker_symbol)

        # RSIを計算
        rsi = calculate_rsi(data)

        # 最新のRSIを取得
        last_rsi = rsi.iloc[-1]

        # 最新のRSIが25未満の場合、LINEで通知を送る
        if last_rsi < 25:
            all_last_rsi_over_25 = False
            message = f"{ticker_symbol}の日足RSIが25を切りました。\n現在のRSI: {last_rsi:.2f}\nチャンス！"
            send_line_notification(message)

    # すべての最新のRSIが25以上の場合、待つことをお勧めするメッセージを送信
    if all_last_rsi_over_25:
        message = "今はまだ待つときです。"
        send_line_notification(message)

def job():
    # 監視するティッカーシンボルのリスト
    ticker_symbols = ["VOO", "VT", "VWO", "SPYD", "HDV", "VYM", "VIG", "SDY"]

    # RSIをチェックし、通知が必要な場合は送信する
    check_rsi_and_notify(ticker_symbols)

# 日本時間0時前後に毎日定期実行するため、UTC時間で15時00分に実行するように設定
# schedule.every().day.at("15:00").do(job)
job()

# 定期実行を開始
# while True:
#     schedule.run_pending()
#     time.sleep(1)

#作成者　中野星七
#作成日　2024/5/24

from flask import Flask, render_template, request
import datetime
import re
import time
import ntplib
import keyboard
from zoneinfo import ZoneInfo
import threading
from dotenv import load_dotenv
import os

# Flaskアプリケーションの作成
app = Flask(__name__)
load_dotenv()

app.config['DEBUG'] = os.environ.get('FLASK_DEBUG')

# 時刻入力パターンの正規表現
time_type = re.compile(r"""
    (                 # 以下、時刻
    (\d{1,2})       # 1 or 2 digits number
    (\D{0,1})
    (\d{1,2})       # 1 or 2 digits number
    (\D{0,1})
    (\d{1,2})       # 1 or 2 digits number
    )
""", re.VERBOSE | re.IGNORECASE)

# 入力された時刻を抽出する関数
def readtime(input):
    input_day = time_type.search(input)
    bool_value = bool(input_day)
    if bool_value is True:
        split = input_day.groups()
        sec = int(split[5])
        min = int(split[3])
        hour = int(split[1])
        if sec < 0 or sec > 59 or min < 0 or min > 59 or hour < 0 or hour > 23:
            print("error:time is invalid")
            return -1, -1, -1
        return hour, min, sec
    else:
        print("error:can't recognize input time")
        return -1, -1, -1

# ホームページ表示
@app.route('/')
def index():
    return render_template('index.html')

# 時刻設定リクエストを処理するエンドポイント
@app.route('/settime', methods=['POST'])
def set_time():
    input_time = request.form['time']
    lag_time = float(request.form['lag_time'])

    # 入力された時刻を読み取り
    hour, minu, sec = readtime(input_time)
    if hour == -1:
        return render_template('result.html', result="Invalid time format")

    # 現在の日時に基づき、ターゲット時刻を設定
    target_time = datetime.datetime.now().replace(hour=hour, minute=minu, second=sec, tzinfo=ZoneInfo(key='Asia/Tokyo'))
    utc_target_time = target_time.astimezone(datetime.timezone.utc)
    ts = datetime.datetime.timestamp(utc_target_time)

    # NTPサーバーから現在時刻を取得
    ntp_client = ntplib.NTPClient()
    ntp_server_host = 'ntp.nict.jp'
    res = ntp_client.request(ntp_server_host)
    waiting = ts - res.tx_time

    # 入力された時刻が過去の場合のエラーハンドリング
    if waiting < 0:
        return render_template('result.html', result="Error: you input past time")

    # 待機時間後にスペースキーを送信する関数
    def wait_and_send_key(waiting, lag_time):
        time.sleep(waiting + lag_time)
        keyboard.send("space")
        print("done")

    # スレッドを使って非同期にキーを送信
    threading.Thread(target=wait_and_send_key, args=(waiting, lag_time)).start()
    return render_template('result.html', result="Time set successfully")

# Flaskアプリケーションの起動
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

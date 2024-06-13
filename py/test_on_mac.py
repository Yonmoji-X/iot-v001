import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import requests

cred = credentials.Certificate('./chiburi-iot-firebase-adminsdk-d750l-5f5a2589c0.json')

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://chiburi-iot-default-rtdb.firebaseio.com/',
    'databaseAuthVariableOverride': {
        'uid': 'my-service-worker'
    }
})



# ===================関数配置=======================
# Lineでメッセージを送る
# ■■■tokenはラズパイでline notify登録してそのtokenに変更してください■■■
def send_line(message):
    url = "https://notify-api.line.me/api/notify"
    token = "rJxCBbDzTbXd6tHHfeCu48UbMW6kXZNzW4mt2ZMpTHJ"
    headers = {"Authorization" : "Bearer "+ token}
    message =  message
    payload = {"message" :  message}
    r = requests.post(url, headers = headers, params=payload)
    print(message);

# 現在地を取得
def get_current_location():
    response = requests.get('http://ipinfo.io')
    data = response.json()
    loc = data['loc'].split(',')
    print(loc);
    return float(loc[0]), float(loc[1])

latitude, longitude = get_current_location()

# 現在地の天気情報を取得
def get_weather(api_key, latitude, longitude):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data)
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        return weather_description, temperature, humidity
    else:
        return None, None

# APIキーと緯度・経度を設定 openWeather
openWeather_api_key = '15c233fe27475d829176b8072ae2adbc'

# 天気情報を取得
weather_description, temperature, humidity = get_weather(openWeather_api_key, latitude, longitude)

# 結果を出力
if weather_description and temperature:
    weather_message = f"\n天気:{weather_description}"
    weather_message += f"\n気温:{temperature}°C"
    weather_message += f"\n湿度:{humidity}"
    # send_line(weather_message);

else:
    print("Failed to fetch weather information.")
    send_line('\n送信エラー\nサポートにご連絡ください。');



#######センサー制御#######


# ================^^^関数配置^^^====================

# ================↓↓↓fireBase処理↓↓↓====================
# ラズパイごとにidはfirebaseを参照して設定する。
theId = '-O-07jvfD3VWg7NQQgi8'
status_ref = db.reference('/led_status')
status_ref_id = db.reference(f'/led_status/{theId}')
status_ref_id_status = db.reference(f'/led_status/{theId}/status')
print(status_ref.get())
print(status_ref_id.get())
print(status_ref_id_status.get())

print(status_ref.get())
# Aの処理を定義
def process_A(raspKey):
    print("Aの処理を実行中...")
    send_line(weather_message);

    # ############→ラズパイ
    sth_ref = db.reference('/sensTempHumi')
    new_sth_ref = sth_ref.push()
    new_sth_key = new_sth_ref.key  # 新しいキーを取得
    data = {
    'raspKey': raspKey,
    'sensTemp': 'sensTemp',
    'sensHumi': 'sensHumi',
    'apiWeather': 'apiWeather',
    'apiTemp': 'apiTemp',
    'apiHumi': 'apiHumi',
    }
    new_sth_ref.set(data)

    print("New Key:", new_sth_key)
    # ############←ラズパイ

    # ここにAの処理を記述する

# データの変更を監視し、変更があった場合にコールバック関数を呼び出す
def callback(event):
    ############→ラズパイ
    key = event.path.split('/')[-1]
    print("key", key)
    print("theId", theId)
    data = event.data
    status = data.get('status')
    if key == theId:
        if status == 'on':
            process_A(key)  # Aの処理を実行
            print("Aの処理作動")
        elif status == 'off':
            # Aの処理を止める
            print("Aの処理を停止しました。")
    ############←ラズパイ

# データの変更を監視開始
status_ref.listen(callback)

# プログラムが終了しないようにするために無限ループを追加
while True:
    time.sleep(1)  # プログラムが終了しないようにするための待機
#     if input("Enterを押して終了します。"):
#         break



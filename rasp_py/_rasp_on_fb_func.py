import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import requests
# Temperature and Humidity Sensor
from logging import getLogger
from time import sleep
import argparse
import smbus

weather_message =  ""
# -----------------------------------sens-temp-humi-----------------------------------
ADDRESS = 0x44

COMMAND_MEAS_HIGHREP = 0x2C
COMMAND_RESULT = 0x00


class SHT31(object):
    def __init__(self, address=ADDRESS):
        self._logger = getLogger(self.__class__.__name__)
        self._address = address
        self._bus = smbus.SMBus(1)

        self._logger.debug("SHT31 sensor is starting...")

    def get_temperature(self):
        """Read the temperature from the sensor and return it."""
        temperature, humidity = self.get_temperature_humidity()
        return temperature

    def get_humidity(self):
        """Read the humidity from the sensor and return it."""
        temperature, humidity = self.get_temperature_humidity()
        return humidity

    def get_temperature_humidity(self):
        self.write_list(COMMAND_MEAS_HIGHREP, [0x06])
        sleep(0.5)

        data = self.read_list(COMMAND_RESULT, 6)
        temperature = -45 + (175 * (data[0] * 256 + data[1]) / 65535.0)
        humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

        return temperature, humidity

    def read(self, register):
        return self._bus.read_byte_data(self._address, register) & 0xFF

    def read_list(self, register, length):
        return self._bus.read_i2c_block_data(
            self._address, register, length)

    def write(self, register, value):
        value = value & 0xFF
        self._bus.write_byte_data(self._address, register, value)

    def write_list(self, register, data):
        self._bus.write_i2c_block_data(self._address, register, data)

def main():
    sensor = SHT31()
    temperature, humidity = sensor.get_temperature_humidity()
    print("Temperature: {} C, Humidity: {} %".format(temperature, humidity))
    return temperature, humidity

#if __name__ == "__main__":
 #   main()



# -----------------------------------firebase-----------------------------------

cred = credentials.Certificate('####################.json')#←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

firebase_admin.initialize_app(cred, {
    'databaseURL': '####################',  #←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
    'databaseAuthVariableOverride': {
        'uid': 'my-service-worker'
    }
})



# ===================????=======================
# Line?????????
# ???token??????line notify??????token????????????
def send_line(message):
    url = "https://notify-api.line.me/api/notify"
    token = ""#←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←api
    headers = {"Authorization" : "Bearer "+ token}
    message =  message
    payload = {"message" :  message}
    r = requests.post(url, headers = headers, params=payload)
    print(message);

# ??????
def get_current_location():
    response = requests.get('http://ipinfo.io')
    data = response.json()
    loc = data['loc'].split(',')
    print(loc);
    return float(loc[0]), float(loc[1])

latitude, longitude = get_current_location()

# ???????????
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

# API??????????? openWeather
openWeather_api_key = ''#←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←api

# ???????
weather_description, temperature, humidity = get_weather(openWeather_api_key, latitude, longitude)

# ?????
if weather_description and temperature:
    #global weather_message
    weather_message += f"\n å¤©æ°:{weather_description}"
    weather_message += f"\næ°æ¸©:{temperature}ã€€â"
    weather_message += f"\næ¹¿åº¦:{humidity}"
    # send_line(weather_message);

else:
    print("Failed to fetch weather information.")
    send_line('\nå¤©æ°æå ±ã®åå¾ã«å¤±æãã¾ããã€');



#######??????#######


# ================^^^????^^^====================

# ================???fireBase?????====================
# ???????id?firebase??????????
theId = '-O-AFrsMRj2zExsnJMvG'
status_ref = db.reference('/led_status')
status_ref_id = db.reference(f'/led_status/{theId}')
status_ref_id_status = db.reference(f'/led_status/{theId}/status')
print(status_ref.get())
print(status_ref_id.get())
print(status_ref_id_status.get())

print(status_ref.get())
# Aã€€ã®å¦ç
def process_A(raspKey):
    print("A???????...")
    sens_temp, sens_humi =  main();
    print(f"\næ¸¬å®æ¸©åº¦:{sens_temp}\næ¸¬å®æ¹¿åº¦:{sens_humi}")
    #######
    sth_ref = db.reference('/sensTempHumi')
    new_sth_ref = sth_ref.push()
    new_sth_key = new_sth_ref.key  # ????????
    data = {
    'raspKey': raspKey,
    'sensTemp': sens_temp,
    'sensHumi': sens_humi,
    'apiWeather': weather_description,
    'apiTemp': temperature,
    'apiHumi': humidity,
    }
    new_sth_ref.set(data)

    print("New Key:", new_sth_key)
    #######
    global weather_message
    weather_message += "ã»ã³ãµã¼æ¸¬å®å€¤"
    weather_message += f"\næ¸¬å®æ¸©åº¦:{sens_temp}"
    weather_message += f"\næ¸¬å®æ¹¿åº¦:{sens_humi}"
    print(weather_message);
    send_line(weather_message);
    # ???A????????

# ?????????????????????????????????
def callback(event):
    ############?????
    key = event.path.split('/')[-1]
    print("key", key)
    print("theId", theId)
    data = event.data
    status = data.get('status')
    if key == theId:
        if status == 'on':
            process_A(key)  # A??????
            print("A?????")
        elif status == 'off':
            # A???????
            print("A???????????")
    ############?????
#
status_ref.listen(callback)

# ã€€å¦çãçµãããªãããã«ç¡éã«ã¼ã
while True:
    time.sleep(1)  #    å¸¸ã«firebaseãç£è¦ã€




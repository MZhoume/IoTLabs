from socket import getaddrinfo, socket
from ussl import wrap_socket
from Keys import *
from machine import Pin
from machine import I2C
from ssd1306 import SSD1306_I2C
import json

lat = '40.8608468'
lng = '-73.8595375'
weather_fahrenheit = ''
weather_desc = ''

GEO_CALL = 'https://www.googleapis.com/geolocation/v1/geolocate?key=%s' % API_KEY
WEATHER_CALL = 'http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s' % (lat, lng, APP_ID)
TWEET_CALL = 'https://api.thingspeak.com/apps/thingtweet/1/statuses/update'

def http_get(url):
    _, _, host, path = url.split('/', 3)
    addr = getaddrinfo(host, 80)[0][-1]
    s = socket()
    s.connect(addr)
    reqstr = 'GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host)
    print(reqstr)
    s.send(bytes(reqstr, 'utf-8'))
    res = []
    while True:
        data = s.recv(100)
        if data:
            res.append(str(data, 'utf-8'))
        else:
            break
    res = ''.join(res)
    i = res.index('{')
    return res[i:]

def http_post(url, payload, useJson):
    print('top of post')
    _, _, host, path = url.split('/', 3)
    print(host + ' ' + path)
    addr = getaddrinfo(host, 443)[0][-1]
    s = socket()
    s.connect(addr)
    s = wrap_socket(s)
    print('wrapped socket')
    reqstr = 'POST /%s HTTP/1.0\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %d\r\n\r\n%s\r\n\r\n' % (path, host, len(payload), payload)
    print('POST: ', reqstr)
    s.write(bytes(reqstr, 'utf-8'))
    res = []
    while True:
        data = s.read(100)
        if data:
            res.append(str(data, 'utf-8'))
        else:
            break
    res = ''.join(res)
    print(res)
    if useJson:
        i = res.index('{')
        return res[i:]
    else:
        return res

def btn_b_pressed(p):
    print('button b pressed')
    http_post(TWEET_CALL, '{"api_key": "%s", "status": "The weather here is %sF. Conditions: %s."}' % (THINGTWEET_API_KEY, weather_fahrenheit, weather_desc), False)

btn_b = Pin(2, Pin.IN, Pin.PULL_UP)
btn_b.irq(trigger=Pin.IRQ_RISING, handler=btn_b_pressed)

disp = SSD1306_I2C(128, 32, I2C(scl=Pin(5), sda=Pin(4), freq=400000))
disp.init_display()

#
##--Get weather information for first time--##
res = http_post(GEO_CALL, '{"considerIp": "true"}', True)
locDic = json.loads(res)
#Set location data
lat = locDic['location']['lat']
lng = locDic['location']['lng']

weather_res = http_get(WEATHER_CALL)
weatherDic = json.loads(weather_res)

#Get weather information
weather_fahrenheit = int(weatherDic['main']['temp']*(9/5) - 459.67)
weather_desc = weatherDic['weather'][0]['description']

disp.text('test', 0,0)
disp.text(weather_desc, 0, 24)
disp.show()
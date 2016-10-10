from socket import getaddrinfo, socket
from ussl import wrap_socket
from Keys import *
from machine import Pin
from machine import I2C
from ssd1306 import SSD1306_I2C
from time import sleep_ms
import json
import gc

lat = ''
lng = ''
temp = ''
desc = ''

GEO_CALL = 'https://www.googleapis.com/geolocation/v1/geolocate?key=%s' % API_KEY
WEATHER_CALL = 'http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s' % (lat, lng, APP_ID)
TWEET_CALL = 'https://api.thingspeak.com/apps/thingtweet/1/statuses/update'

def http_get(url):
    gc.collect()
    _, _, host, path = url.split('/', 3)
    addr = getaddrinfo(host, 80)[0][-1]
    s = socket()
    s.connect(addr)
    reqstr = 'GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host)
    s.send(bytes(reqstr, 'utf-8'))
    gc.collect()
    res = []
    while True:
        data = s.recv(100)
        if data:
            res.append(str(data, 'utf-8'))
        else:
            break

    s.close()
    gc.collect()
    return ''.join(res)

def http_post(url, payload):
    gc.collect()
    _, _, host, path = url.split('/', 3)
    addr = getaddrinfo(host, 443)[0][-1]
    s = socket()
    s.connect(addr)
    s = wrap_socket(s)
    reqstr = 'POST /%s HTTP/1.0\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %d\r\n\r\n%s\r\n\r\n' % (path, host, len(payload), payload)
    s.write(bytes(reqstr, 'utf-8'))
    gc.collect()
    res = []
    while True:
        data = s.read(100)
        if data:
            res.append(str(data, 'utf-8'))
        else:
            break

    s.close()
    gc.collect()
    return ''.join(res)

def btn_b_pressed(p):
    print('button b pressed')
    # http_post(TWEET_CALL, '{"api_key": "%s", "status": "The weather here is %sF. Conditions: %s."}' % (THINGTWEET_API_KEY, weather_fahrenheit, weather_desc), False)

btn_b = Pin(2, Pin.IN, Pin.PULL_UP)
btn_b.irq(trigger=Pin.IRQ_RISING, handler=btn_b_pressed)

disp = SSD1306_I2C(128, 32, I2C(scl=Pin(5), sda=Pin(4), freq=400000))
disp.init_display()

res = http_post(GEO_CALL, '{"considerIp": "true"}')
geoJson = json.loads(res[res.index('{'):])
gc.collect()
lat = locDic['location']['lat']
lng = locDic['location']['lng']
print('lat = %s, lng = %s' % (lat, lng))
gc.collect()

res = http_get(WEATHER_CALL)
weaJson = json.loads(res[res.index('{'):])
gc.collect()
temp = weatherDic['main']['temp']
desc = weatherDic['weather'][0]['description']
print('temp = %s, desc = %s' % (temp, desc))

geoStr = 'G %.2f %.2f' % (lat, lng)
weaStr = 'T %s\r\nD %s' % (temp, desc)
disp.text(geoStr, 0,0)
disp.text(weaStr, 0, 16)
disp.show()

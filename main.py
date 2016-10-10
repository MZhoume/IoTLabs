from socket import getaddrinfo, socket
from ussl import wrap_socket
from Keys import *
from json import loads
import gc

addr = getaddrinfo('www.googleapis.com', 443)[0][-1]
s = socket()
s.connect(addr)
gc.collect()
s = wrap_socket(s)
gc.collect()
reqstr = 'POST /geolocation/v1/geolocate?key=%s HTTP/1.0\r\nHost: www.googleapis.com\r\nContent-Type: application/json\r\nContent-Length: 22\r\n\r\n{"considerIp": "true"}\r\n\r\n' % API_KEY
s.write(bytes(reqstr, 'utf-8'))
res = []
gc.collect()
while True:
    data = s.read(100)
    if data:
        res.append(str(data, 'utf-8'))
    else:
        break

s.close()
gc.collect()
res = ''.join(res)

geoJson = loads(res[res.index('{'):])
gc.collect()
lat = geoJson['location']['lat']
lng = geoJson['location']['lng']
print('lat = %s, lng = %s' % (lat, lng))
gc.collect()

addr = getaddrinfo('api.openweathermap.org', 80)[0][-1]
s = socket()
s.connect(addr)
gc.collect()
reqstr = 'GET /data/2.5/weather?lat=%s&lon=%s&appid=%s HTTP/1.0\r\nHost: api.openweathermap.org\r\n\r\n' % (lat, lng, APP_ID)
s.send(bytes(reqstr, 'utf-8'))
res = []
gc.collect()
while True:
    data = s.recv(100)
    if data:
        res.append(str(data, 'utf-8'))
    else:
        break

s.close()
gc.collect()
res = ''.join(res)

weaJson = loads(res[res.index('{'):])
gc.collect()
temp = int(weaJson['main']['temp']) - 273
desc = weaJson['weather'][0]['description']
print('temp = %s, desc = %s' % (temp, desc))
gc.collect()

from machine import Pin
from machine import I2C
from ssd1306 import SSD1306_I2C
from time import sleep_ms

def btn_b_pressed(p):
    gc.collect()
    addr = getaddrinfo('api.thingspeak.com', 443)[0][-1]
    s = socket()
    s.connect(addr)
    s = wrap_socket(s)
    gc.collect()
    t = '{"api_key": "%s", "status": "The weather here is %sC, %s."}' % (THINGTWEET_API_KEY, temp, desc)
    reqstr = 'POST /apps/thingtweet/1/statuses/update HTTP/1.0\r\nHost: api.thingspeak.com\r\nContent-Type: application/json\r\nContent-Length: %d\r\n\r\n%s\r\n\r\n' % (len(t), t)
    s.write(bytes(reqstr, 'utf-8'))
    s.close()
    gc.collect()
    print('tweeted')

btn_b = Pin(2, Pin.IN, Pin.PULL_UP)
btn_b.irq(trigger=Pin.IRQ_RISING, handler=btn_b_pressed)

disp = SSD1306_I2C(128, 32, I2C(scl=Pin(5), sda=Pin(4), freq=400000))
disp.init_display()

geoStr = 'G %.2f %.2f' % (lat, lng)
weaStr = '%.2fC, %s' % (temp, desc)
disp.text(geoStr, 0, 0)
disp.text(weaStr, 0, 16)
disp.show()

while True:
    sleep_ms(5000)
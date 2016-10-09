from Keys import *
from machine import Pin
from machine import I2C
from ssd1306 import SSD1306_I2C
from time import sleep_ms
import json

lat = ''
lon = ''

GEO_CALL = 'https://www.googleapis.com/geolocation/v1/geolocate?key=%s' % API_KEY
WEATHER_CALL = 'http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s' % (lat, lon, APP_ID)
TWEET_CALL = 'https://api.thingspeak.com/apps/thingtweet/1/statuses/update'

class SocketWrapper:
    def __init__(self, socket, https = False):
        self.https = https
        if https:
            from ussl import wrap_socket
            self.socket = wrap_socket(socket)
        else:
            self.socket = socket

    def send(self, payload):
        if self.https:
            self.socket.write(bytes(payload, 'utf-8'))
        else:
            self.socket.send(bytes(payload, 'utf-8'))

    def recv(self, num):
        if self.https:
            return str(self.socket.read(num), 'utf-8')
        else:
            return str(self.socket.recv(num), 'utf-8')

class WrappedSocket:
    def __init__(self, url, https = False):
        from socket import getaddrinfo, socket
        _, _, host, path = url.split('/', 3)
        self.host = host
        self.path = path
        addr = getaddrinfo(host, 80 if not https else 443)[0][-1]
        soc = socket()
        soc.connect(addr)
        self.socket = SocketWrapper(soc, https)

    def close(self):
        self.socket.close()

    def get(self):
        reqStr = 'GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (self.path, self.host)
        print(reqStr)
        self.socket.send(reqstr)
        res = []
        while True:
            data = self.socket.recv(100)
            if data:
                res.append(data)
            else:
                break
        return ''.join(res)

    def post(self, payload):
        reqStr = 'POST /%s HTTP/1.0\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %d\r\n\r\n%s\r\n\r\n' % (self.path, self.host, len(payload), payload)
        print(reqStr)
        self.send(reqStr)
        res = []
        while True:
            data = self.socket.recv(100)
            if data:
                res.append(data)
            else:
                break
        return ''.join(res)

def btn_b_pressed(p):
    print('button b pressed')
    

btn_b = Pin(2, Pin.IN, Pin.PULL_UP)
btn_b.irq(trigger=Pin.IRQ_RISING, handler=btn_b_pressed)

disp = SSD1306_I2C(128, 32, I2C(scl=Pin(5), sda=Pin(4), freq=400000))
disp.init_display()

geoSoc = WrappedSocket(GEO_CALL, True)
weaSoc = WrappedSocket(WEATHER_CALL, False)
twtSoc = WrappedSocket(TWEET_CALL, True)

geoRes = geoSoc.post('{"considerIp": "true"}')
geo = json.loads(geoRes[geoRes.index('{'):])
print(geo)

lat = locDic['location']['lat']
lon = locDic['location']['lng']

weaRes = weaSoc.get()
weather = json.loads(weaRes[weaRes.index('{'):])

temp = int(weather['main']['temp'])
desc = weather['weather'][0]['description']

locStr = 'Loc: %.2f %.2f' % (lat, lng)
weaStr = 'Wea: %d %s' % (temp, desc)
disp.text(locStr, 0, 0)
disp.text(weaStr, 0, 16)
disp.show()

twtRes = twtSoc.post('{"api_key": "%s", "status": "The weather here is %sC. Conditions: %s."}' % (THINGTWEET_API_KEY, temp, desc))

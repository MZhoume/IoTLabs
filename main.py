from socket import getaddrinfo, socket
from ussl import wrap_socket
from Keys import *
import json

lat = '40.8138912'
lon = '-73.96243270000001'

GEO_CALL = 'https://www.googleapis.com/geolocation/v1/geolocate?key=%s' % API_KEY
WEATHER_CALL = 'http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s' % (lat, lon, APP_ID)

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

def http_post(url, payload):
    _, _, host, path = url.split('/', 3)
    addr = getaddrinfo(host, 443)[0][-1]
    s = socket()
    s.connect(addr)
    s = wrap_socket(s)
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
    print(res)
    res = ''.join(res)
    i = res.index('{')
    return res[i:]

res = http_post(GEO_CALL, '{"considerIp": "true"}')
print(res)
print(json.loads(res))
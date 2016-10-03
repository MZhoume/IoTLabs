from network import *

class WIFI(object):
    def __init__(self):
        sta = WLAN(STA_IF)
        if not sta.isconnected():
            print('Connecting to wifi...')
            sta.active(True)
            sta.connect('Columbia University', '')
            while not sta.isconnected():
                pass
        print('Connected...', sta.ifconfig())

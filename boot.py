# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import gc
import webrepl
from network import WLAN, STA_IF
from machine import Pin

webrepl.start()

sta = WLAN(STA_IF)
if not sta.isconnected():
    print('Connecting to wifi...')
    sta.active(True)
    sta.connect('Columbia University', '')
    while not sta.isconnected():
        pass
print('Connected...', sta.ifconfig())
p = Pin(0, Pin.OUT)
p.low()

gc.collect()

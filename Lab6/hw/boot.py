# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import gc
import webrepl
from network import WLAN, STA_IF

webrepl.start()

sta = WLAN(STA_IF)
if not sta.isconnected():
    sta.active(True)
    sta.connect('Columbia University', '')
    while not sta.isconnected():
        pass

gc.collect()

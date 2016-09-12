import time
from machine import Pin

def on(p):
    p.low()

def off(p):
    p.high()

def togglep0():
    for i in range(5):
        on(p0)
        time.sleep_ms(100)
        off(p0)
        time.sleep_ms(100)

p0 = Pin(0, Pin.OUT)
p2 = Pin(2, Pin.OUT)

while True:
    on(p2)
    togglep0()
    off(p2)
    togglep0()
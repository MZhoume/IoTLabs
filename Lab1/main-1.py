import time
from machine import Pin

def on(p):
    p.low()

def off(p):
    p.high()

def blink3(l, t):
    for i in range(3):
        on(l)
        time.sleep_ms(t)
        off(l)
        time.sleep_ms(t)

p = Pin(2, Pin.OUT)

while True:
    blink3(p, 300)
    blink3(p, 600)
    blink3(p, 300)
    time.sleep_ms(5000)
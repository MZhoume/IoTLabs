import time
from machine import Pin

def blink(l, t):
    for i in range(3):
        l.low()
        time.sleep_ms(t)
        l.high()
        time.sleep_ms(t)

p = Pin(2, Pin.OUT)
while True:
    blink(p, 300)
    blink(p, 600)
    blink(p, 300)
    time.sleep_ms(5000)
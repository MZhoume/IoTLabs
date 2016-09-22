from time import sleep_ms
from machine import Pin

def on(l):
    l.low()

def off(l):
    l.high()

def blinkLED0():
    # blink LED #0 in the inner loop (faster)
    for i in range(5):
        on(led0)
        sleep_ms(50)
        off(led0)
        sleep_ms(50)

# ===========================================================
led0 = Pin(0, Pin.OUT)
led1 = Pin(2, Pin.OUT)

# blink LED #1 in the outer loop (slower)
while True:
    on(led1)
    blinkLED0()
    off(led1)
    blinkLED0()
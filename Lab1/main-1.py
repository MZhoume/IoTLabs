# morse code for SOS is:
# dot x 3, dash x 3, dot x 3
#   (S)      (O)      (S)

from time import sleep_ms
from machine import Pin

def on(l):
    l.low()

def off(l):
    l.high()

def blink3x(l, t):
    for i in range(3):
        on(l)
        sleep_ms(t)
        off(l)
        sleep_ms(t)

# ===========================================================
led1 = Pin(2, Pin.OUT)

while True:
    # blinks the ...
    blink3x(led1, 300)

    # blinks the ---
    blink3x(led1, 600)

    # blinks the ..., again
    blink3x(led1, 300)

    # and some break
    sleep_ms(5000)
from machine import RTC
from machine import Pin
from machine import SPI
from machine import I2C
from ssd1306 import SSD1306_I2C
from time import sleep_ms
import math

def spi_read(addr):
    cs.low()
    sleep_ms(5)
    spi.write(addr)
    sleep_ms(5)
    d = spi.read(1)
    sleep_ms(5)
    cs.high()
    return d

def spi_write(addr, data):
    cs.low()
    sleep_ms(5)
    spi.write(addr)
    sleep_ms(5)
    spi.write(data)
    sleep_ms(5)
    cs.high()

direction = 0
pos_x = 0
pos_y = 0

def btn_a_pressed(p):
    global direction
    direction = (direction + 1) % 4

btn_a = Pin(14, Pin.IN, Pin.PULL_UP)
btn_a.irq(trigger=Pin.IRQ_RISING, handler=btn_a_pressed)

rtc = RTC()
rtc.datetime((2016, 1, 1, 0, 0, 1, 0, 0))

disp = SSD1306_I2C(128, 32, I2C(scl=Pin(5), sda=Pin(4), freq=400000))
disp.init_display()

cs = Pin(0, Pin.OUT)
cs.high()
spi = SPI(-1, baudrate=9600, polarity=1, phase=1, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
spi.init()

while True:
    y, m, d, t1, hh, mm, ss, t2 = rtc.datetime()

    time = '{}{}{} {}{}{}'.format(hh if hh >= 10 else '0{}'.format(hh), 
        mm if mm >= 10 else '0{}'.format(mm), 
        ss if ss >= 10 else '0{}'.format(ss), 
        y % 1000,
        m if m >= 10 else '0{}'.format(m), 
        d if d >= 10 else '0{}'.format(d))
    
    disp.fill(0)
    disp.text(time, pos_x, pos_y)
    if direction == 0:
        pos_x = pos_x + 1 if pos_x < 128 else -128
    elif direction == 1:
        pos_x = pos_x - 1 if pos_x > -128 else 128
    elif direction == 2:
        pos_y = pos_y + 1 if pos_y < 32 else -8
    elif direction == 3:
        pos_y = pos_y - 1 if pos_y > -8 else 32
    disp.show()

    sleep_ms(50)

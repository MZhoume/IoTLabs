from machine import RTC
from machine import Pin
from machine import I2C
from machine import ADC
from ssd1306 import SSD1306_I2C
from ad345 import AD345
from time import sleep_ms

# initializing components
rtc = RTC()
rtc.datetime((2016, 1, 1, 0, 0, 0, 0, 0))

disp = SSD1306_I2C(128, 32, I2C(scl=Pin(5), sda=Pin(4), freq=400000))
disp.init_display()

spi = AD345()

adc = ADC(0)

# global variable
pos_x = 0
pos_y = 0

while True:

    # get time and date and format them into proper string
    y, m, d, t1, hh, mm, ss, t2 = rtc.datetime()
    time = '{}:{}:{}'.format(hh if hh >= 10 else '0{}'.format(hh), 
        mm if mm >= 10 else '0{}'.format(mm), 
        ss if ss >= 10 else '0{}'.format(ss))    
    date = '{}/{}/{}'.format(y % 1000,
        m if m >= 10 else '0{}'.format(m), 
        d if d >= 10 else '0{}'.format(d))
    
    # set the contrast accrding to adc readout
    adc_val = adc.read()
    disp.contrast(adc_val if adc_val < 1024 else adc_val - 1)

    # draw text to the display
    disp.fill(0)
    disp.text(time, pos_x, pos_y)
    disp.text(date, pos_x, pos_y + 8)
    disp.show()

    # get the ad345 data
    x, y, z = spi.xyz()

    # tilting to the right
    if x > 4 and y > 4:
        pos_x = pos_x + 1 if pos_x < 128 else -64
    
    # tilting to the left
    elif x < 4 and y < 4:
        pos_x = pos_x - 1 if pos_x > -64 else 128

    # tilting to bottom
    elif x > 4 and y < 4:
        pos_y = pos_y + 1 if pos_y < 32 else -16
    
    # tilting to top
    elif x < 4 and y > 4:
        pos_y = pos_y - 1 if pos_y > -16 else 32

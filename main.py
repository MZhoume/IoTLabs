from machine import RTC
from machine import Pin
from ssd1306a import SSD1306
from time import sleep_ms
import math


rtc = RTC()
rtc.datetime((2016, 1, 1, 0, 0, 1, 0, 0))

disp = SSD1306()
disp.init_display()

while True:
    y, m, d, t1, hh, mm, ss, t2 = rtc.datetime()

    time = '{}:{}:{} {}/{}/{}'.format(hh if hh >= 10 else '0{}'.format(hh), mm if mm >= 10 else '0{}'.format(mm), ss if ss >= 10 else '0{}'.format(ss), 
            y % 1000, m if m >= 10 else '0{}'.format(m), d if d >= 10 else '0{}'.format(d))

    
    disp.clear()
    disp.draw_text(0, 0, time)
    disp.display()




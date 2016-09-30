from machine import RTC
from machine import Pin
from machine import ADC
from ssd1306a import SSD1306
from time import sleep_ms

temp_hh = 0
temp_mm = 0
temp_ss = 0

is_changing = False
part_changing = -1

btn_a = Pin(0, Pin.IN, Pin.PULL_UP)
btn_a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=btn_a_pressed)
btn_b = Pin(16, Pin.IN, Pin.PULL_UP)
btn_b.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=btn_b_pressed)
btn_c = Pin(2, Pin.IN, Pin.PULL_UP)
btn_c.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=btn_c_pressed)

# loops through the hours, minutes, and seconds and highlights the value to be edited
def btn_a_pressed(p):
    is_changing = True
    part_changing = (part_changing + 1) % 3

# changes the value currently highlighted
def btn_b_pressed(p):
    

# confirms any changes to the time
def btn_c_pressed(p):
    is_changing = False
    part_changing = -1

adc = ADC(0)

rtc = RTC()
rtc.datetime((2016, 9, 6, 0, 0, 0, 0, 0))

disp = SSD1306()
disp.init_display()

while True:
    y, m, d, t1, hh, mm, ss, t2 = rtc.datetime()
    time = '{}/{}/{} {}:{}:{}'.format(y, m, d, hh, mm if mm > 10 else '0{}'.format(mm), ss if ss > 10 else '0{}'.format(ss))
    disp.clear()
    disp.draw_text(0, 0, time)
    disp.display()
    sleep_ms(100)

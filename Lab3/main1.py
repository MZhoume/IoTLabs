from machine import RTC
from machine import Pin
from machine import ADC
from ssd1306a import SSD1306
from time import sleep_ms

# loops through the hours, minutes, and seconds and highlights the value to be edited
def btn_a_pressed(p):
    global is_changing
    global part_changing
    is_changing = True
    part_changing = (part_changing + 1) % 3
    print(is_changing, part_changing)

# changes the value currently highlighted
def btn_b_pressed(p):
    global part_changing
    global temp_hh
    global temp_mm
    global temp_ss
    if part_changing == 0:
        temp_hh = (temp_hh +1) % 24
    if part_changing == 1:
        temp_mm = (temp_mm +1) % 60
    if part_changing == 2:
        temp_ss = (temp_ss +1) % 60

# confirms any changes to the time
def btn_c_pressed(p):
    global is_changing
    global part_changing
    global rtc
    global has_changed
    is_changing = False
    part_changing = -1
    has_changed = True

indicator = '**'

temp_hh = 0
temp_mm = 0
temp_ss = 0

is_changing = False
part_changing = -1
has_changed = False

adc = ADC(0)

rtc = RTC()
rtc.datetime((2016, 9, 6, 0, 0, 0, 0, 0))

disp = SSD1306()
disp.init_display()

btn_a = Pin(14, Pin.IN, Pin.PULL_UP)
btn_a.irq(trigger=Pin.IRQ_RISING, handler=btn_a_pressed)
btn_b = Pin(12, Pin.IN, Pin.PULL_UP)
btn_b.irq(trigger=Pin.IRQ_RISING, handler=btn_b_pressed)
btn_c = Pin(13, Pin.IN, Pin.PULL_UP)
btn_c.irq(trigger=Pin.IRQ_RISING, handler=btn_c_pressed)

while True:
    if has_changed:
        y, m, d, t1, hh, mm, ss, t2 = rtc.datetime()
        rtc.datetime((y, m, d, 0, temp_hh, temp_mm, temp_ss, 0))
        temp_hh = temp_mm = temp_ss = 0
        has_changed = False

    y, m, d, t1, hh, mm, ss, t2 = rtc.datetime()

    t_hh = hh if not is_changing else temp_hh
    t_mm = mm if not is_changing else temp_mm
    t_ss = ss if not is_changing else temp_ss

    time = '{}:{}:{}  {}/{}/{}'.format(t_hh if t_hh >= 10 else '0{}'.format(t_hh), t_mm if t_mm >= 10 else '0{}'.format(t_mm), t_ss if t_ss >= 10 else '0{}'.format(t_ss), y, m, d)
    disp.clear()
    disp.draw_text(0, 0, time)
    if is_changing:
        disp.draw_text(17 * part_changing + part_changing, 8, indicator)
    disp.display()
    







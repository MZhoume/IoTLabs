from machine import RTC
from machine import Pin
from machine import ADC
from machine import PWM
from machine import I2C
from ssd1306 import SSD1306_I2C
from time import sleep_ms

indicator = '^^'

temp_hh = 0
temp_mm = 0
temp_ss = 0
temp_m  = 1
temp_d  = 1
temp_y  = 2016

alarm_hh = 0
alarm_mm = 1
alarm_ss = 0
alarm_m  = 1
alarm_d  = 1
alarm_y  = 2016

is_setting_alarm = False
is_setting_time = False
part_changing = -1
has_changed_time = False
has_changed_alarm = False

# in setting time mode: loop through elements;
# in setting alarm mode: confirm change
def btn_a_pressed(p):
    global part_changing
    global is_setting_time
    global is_setting_alarm
    global has_changed_alarm

    if is_setting_alarm:
        part_changing = -1
        is_setting_alarm = False
        has_changed_alarm = True
    else:
        is_setting_time = True
        part_changing = (part_changing + 1) % 6

# add 1 to the current element
def btn_b_pressed(p):
    global part_changing
    global temp_hh
    global temp_mm
    global temp_ss
    global alarm_hh
    global alarm_mm

    if is_setting_time:
        if part_changing == 0:
            temp_hh = (temp_hh +1) % 24
        elif part_changing == 1:
            temp_mm = (temp_mm +1) % 60
        elif part_changing == 2:
            temp_ss = (temp_ss +1) % 60
        elif part_changing == 3:
            temp_y = (temp_y +1) % 2100
        elif part_changing == 4:
            temp_m = (temp_m +1) % 13
        elif part_changing == 5:
            temp_d = (temp_d +1) % 32
    elif is_setting_alarm:
        if part_changing == 0:
            alarm_hh = (alarm_hh +1) % 24
        elif part_changing == 1:
            alarm_mm = (alarm_mm +1) % 60
        elif part_changing == 2:
            alarm_ss = (alarm_ss +1) % 60
        elif part_changing == 3:
            alarm_y = (alarm_y +1) % 2100
        elif part_changing == 4:
            alarm_m = (alarm_m +1) % 13
        elif part_changing == 5:
            alarm_d = (alarm_d +1) % 32

# in setting alarm mode: loop through elements;
# in setting time mode: confirm change
def btn_c_pressed(p):
    global part_changing
    global has_changed_time
    global is_setting_alarm
    global is_setting_time

    if is_setting_time:
        is_setting_time = False
        part_changing = -1
        has_changed_time = True
    else:
        is_setting_alarm = True
        part_changing = (part_changing + 1) % 6

adc = ADC(0)

rtc = RTC()
rtc.datetime((2016, 1, 1, 0, 0, 1, 0, 0))

disp = SSD1306_I2C(128, 32, I2C(scl=Pin(5), sda=Pin(4), freq=400000))
disp.init_display()

btn_a = Pin(14, Pin.IN, Pin.PULL_UP)
btn_a.irq(trigger=Pin.IRQ_RISING, handler=btn_a_pressed)
btn_b = Pin(2, Pin.IN, Pin.PULL_UP)
btn_b.irq(trigger=Pin.IRQ_RISING, handler=btn_b_pressed)
btn_c = Pin(13, Pin.IN, Pin.PULL_UP)
btn_c.irq(trigger=Pin.IRQ_RISING, handler=btn_c_pressed)

piezo_pin = PWM(Pin(15))
piezo_pin.freq(1000)
piezo_pin.duty(0)

while True:
    if has_changed_time:
        rtc.datetime((temp_y, temp_m, temp_d, 0, temp_hh, temp_mm, temp_ss, 0))
        temp_hh = temp_mm = temp_ss = 0
        temp_y = 2016
        temp_m = temp_d = 1
        has_changed_time = False
    elif has_changed_alarm:
        has_changed_alarm = False

    y, m, d, t1, hh, mm, ss, t2 = rtc.datetime()

    if is_setting_time:
        t_hh = temp_hh
        t_mm = temp_mm
        t_ss = temp_ss
        t_y = temp_y
        t_m = temp_m
        t_d = temp_d
    else:
        t_hh = hh
        t_mm = mm
        t_ss = ss
        t_y = y
        t_m = m
        t_d = d

    if is_setting_alarm: 
        time = '{}{}{} {}{}{}A'.format(alarm_hh if alarm_hh >= 10 else '0{}'.format(alarm_hh), 
            alarm_mm if alarm_mm >= 10 else '0{}'.format(alarm_mm), 
            alarm_ss if alarm_ss >= 10 else '0{}'.format(alarm_ss), 
            alarm_y % 1000, 
            alarm_m if alarm_m >= 10 else '0{}'.format(alarm_m), 
            alarm_d if alarm_d >= 10 else '0{}'.format(alarm_d))
    else:
        time = '{}{}{} {}{}{}'.format(t_hh if t_hh >= 10 else '0{}'.format(t_hh), 
            t_mm if t_mm >= 10 else '0{}'.format(t_mm), 
            t_ss if t_ss >= 10 else '0{}'.format(t_ss), 
            t_y % 1000, 
            t_m if t_m >= 10 else '0{}'.format(t_m), 
            t_d if t_d >= 10 else '0{}'.format(t_d))

    disp.fill(0)
    disp.text(time, 0, 0)
    if is_setting_time or is_setting_alarm:
        disp.text(indicator, 16 * part_changing + (8 if part_changing > 2 else 0), 8)
    
    adc_val = adc.read()
    disp.contrast(adc_val if adc_val < 1024 else adc_val - 1)
    disp.show()

    if not is_setting_alarm and (hh == alarm_hh and mm == alarm_mm and ss == alarm_ss and y == alarm_y and m == alarm_m and d == alarm_d):
        piezo_pin.duty(500)
        disp.fill(0)
        disp.invert(True)
        sleep_ms(5000)
        piezo_pin.duty(0)
        disp.invert(False)

    sleep_ms(100)

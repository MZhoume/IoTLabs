from machine import RTC
from machine import Pin
from machine import ADC
from machine import PWM
from ssd1306a import SSD1306
from time import sleep_ms

# loops through the hours, minutes, and seconds and highlights the value to be edited
def btn_a_pressed(p):
    global part_changing
    global is_changing
    global is_setting_alarm

    if is_setting_alarm:
        part_changing = -1
        is_setting_alarm = False
        has_changed_alarm = True
        print('set alarm')
    else:
        is_changing = True
        part_changing = (part_changing + 1) % 6
        print('is changing')

# changes the value currently highlighted
def btn_b_pressed(p):
    global part_changing
    global temp_hh
    global temp_mm
    global temp_ss
    global alarm_hh
    global alarm_mm

    if is_changing:
        if part_changing == 0:
            temp_hh = (temp_hh +1) % 24
        if part_changing == 1:
            temp_mm = (temp_mm +1) % 60
        if part_changing == 2:
            temp_ss = (temp_ss +1) % 60
        if part_changing == 3:
            temp_y = (temp_y +1) % 2100
        if part_changing == 4:
            temp_m = (temp_m +1) % 13
        if part_changing == 5:
            temp_d = (temp_d +1) % 32
    elif is_setting_alarm:
        if part_changing == 0:
            alarm_hh = (alarm_hh +1) % 24
        if part_changing == 1:
            alarm_mm = (alarm_mm +1) % 60
        if part_changing == 2:
            alarm_ss = (alarm_ss +1) % 60
        if part_changing == 3:
            alarm_y = (alarm_y +1) % 2100
        if part_changing == 4:
            alarm_m = (alarm_m +1) % 13
        if part_changing == 5:
            alarm_d = (alarm_d +1) % 32


# confirms any changes to the time
def btn_c_pressed(p):
    global is_setting_alarm
    global part_changing
    global is_changing
    global has_changed

    if is_changing:
        is_changing = False
        part_changing = -1
        has_changed = True
    else:
        is_setting_alarm = True
        part_changing = (part_changing + 1) % 6

indicator = '**'

temp_hh = 0
temp_mm = 0
temp_ss = 0
temp_m  = 1
temp_d  = 1
temp_y  = 2016

alarm_hh = 0
alarm_mm = 0
alarm_ss = 0
alarm_m  = 1
alarm_d  = 1
alarm_y  = 2016

is_changing = False
part_changing = -1
has_changed = False
has_changed_alarm = False
is_setting_alarm = False

adc = ADC(0)

rtc = RTC()
rtc.datetime((2016, 1, 1, 0, 0, 1, 0, 0))

disp = SSD1306()
disp.init_display()

btn_a = Pin(14, Pin.IN, Pin.PULL_UP)
btn_a.irq(trigger=Pin.IRQ_RISING, handler=btn_a_pressed)
btn_b = Pin(12, Pin.IN, Pin.PULL_UP)
btn_b.irq(trigger=Pin.IRQ_RISING, handler=btn_b_pressed)
btn_c = Pin(13, Pin.IN, Pin.PULL_UP)
btn_c.irq(trigger=Pin.IRQ_RISING, handler=btn_c_pressed)

piezo_pin = PWM(Pin(15))
piezo_pin.freq(1000)
piezo_pin.duty(0)

while True:
    if has_changed:
        rtc.datetime((temp_y, temp_m, temp_d, 0, temp_hh, temp_mm, temp_ss, 0))
        temp_hh = temp_mm = temp_ss = 0
        temp_y = 2016
        temp_m = temp_d = 1
        has_changed = False
    elif has_changed_alarm: 
        y, m, d, t1, hh, mm, ss, t2 = rtc.datetime()
        has_changed_alarm = False


    y, m, d, t1, hh, mm, ss, t2 = rtc.datetime()

    t_hh = hh if not is_changing else temp_hh
    t_mm = mm if not is_changing else temp_mm
    t_ss = ss if not is_changing else temp_ss
    t_y = y if not is_changing else temp_y
    t_m = m if not is_changing else temp_m
    t_d = d if not is_changing else temp_d

    if is_setting_alarm: 
        time = '{}:{}:{} {}/{}/{}A'.format(alarm_hh if alarm_hh >= 10 else '0{}'.format(alarm_hh), alarm_mm if alarm_mm >= 10 else '0{}'.format(alarm_mm), alarm_ss if alarm_ss >= 10 else '0{}'.format(alarm_ss), 
            alarm_y % 1000, alarm_m if alarm_m >= 10 else '0{}'.format(alarm_m), alarm_d if alarm_d >= 10 else '0{}'.format(alarm_d))

    else:
        time = '{}:{}:{} {}/{}/{}'.format(t_hh if t_hh >= 10 else '0{}'.format(t_hh), t_mm if t_mm >= 10 else '0{}'.format(t_mm), t_ss if t_ss >= 10 else '0{}'.format(t_ss), 
            t_y % 1000, t_m if t_m >= 10 else '0{}'.format(t_m), t_d if t_d >= 10 else '0{}'.format(t_d))
    
    disp.clear()
    disp.draw_text(0, 0, time)
    if is_changing or is_setting_alarm:
        disp.draw_text(17 * part_changing + part_changing, 8, indicator)
    
    adc_val = adc.read()
    disp.contrast(adc_val if adc_val < 1024 else adc_val - 1)
    disp.display()

    if not is_setting_alarm and (hh == alarm_hh and mm == alarm_mm and (ss - alarm_ss) <= 3 and y == alarm_y and m == alarm_m and d == alarm_d):
        piezo_pin.duty(500)
        disp.clear()
        disp.invert_display(True)
        disp.display()
        sleep_ms(5000)
        piezo_pin.duty(0)
        disp.invert_display(False)




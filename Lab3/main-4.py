from machine import RTC
from machine import Pin
from machine import ADC
from machine import PWM
from machine import I2C
from ssd1306 import SSD1306_I2C
from time import sleep_ms

# global variables
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

# global flags
is_setting_alarm = False
is_setting_time = False
part_changing = -1
has_changed_time = False

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
    else:
        is_setting_time = True
        part_changing = (part_changing + 1) % 6

# add 1 to the current value
def btn_b_pressed(p):
    global part_changing
    global temp_hh
    global temp_mm
    global temp_ss
    global temp_m 
    global temp_d 
    global temp_y
    global alarm_hh
    global alarm_mm
    global alarm_ss
    global alarm_m 
    global alarm_d 
    global alarm_y 

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
        part_changing = -1
        is_setting_time = False
        has_changed_time = True
    else:
        is_setting_alarm = True
        part_changing = (part_changing + 1) % 6

# initializing components
adc = ADC(0)

piezo_pin = PWM(Pin(15))
piezo_pin.freq(1000)
piezo_pin.duty(0)

rtc = RTC()
rtc.datetime((2016, 1, 1, 0, 0, 0, 0, 0))

disp = SSD1306_I2C(128, 32, I2C(scl=Pin(5), sda=Pin(4), freq=400000))
disp.init_display()

btn_a = Pin(14, Pin.IN, Pin.PULL_UP)
btn_a.irq(trigger=Pin.IRQ_RISING, handler=btn_a_pressed)
btn_b = Pin(2, Pin.IN, Pin.PULL_UP)
btn_b.irq(trigger=Pin.IRQ_RISING, handler=btn_b_pressed)
btn_c = Pin(13, Pin.IN, Pin.PULL_UP)
btn_c.irq(trigger=Pin.IRQ_RISING, handler=btn_c_pressed)

while True:

    # if time changed, reset the rtc
    if has_changed_time:
        rtc.datetime((temp_y, temp_m, temp_d, 0, temp_hh, temp_mm, temp_ss, 0))
        temp_hh = temp_mm = temp_ss = 0
        temp_y = 2016
        temp_m = temp_d = 1
        has_changed_time = False

    # readout current time
    y, m, d, t1, hh, mm, ss, t2 = rtc.datetime()

    # if current time matches alarm time, alert
    if not is_setting_alarm and (hh == alarm_hh and mm == alarm_mm and ss == alarm_ss and y == alarm_y and m == alarm_m and d == alarm_d):
        piezo_pin.duty(500)
        disp.fill(0)
        disp.invert(True)
        disp.show()
        sleep_ms(5000)
        piezo_pin.duty(0)
        disp.invert(False)
        disp.show()

        # reset the alarm value
        alarm_hh = alarm_mm = alarm_ss = 0
        alarm_y = 2016
        alarm_m = alarm_d = 1
    
    # compose right time and date to display
    if is_setting_alarm: 
        time = 'AT: {}:{}:{} {}'.format(alarm_hh if alarm_hh >= 10 else '0{}'.format(alarm_hh), 
            alarm_mm if alarm_mm >= 10 else '0{}'.format(alarm_mm), 
            alarm_ss if alarm_ss >= 10 else '0{}'.format(alarm_ss),
            '<' if part_changing < 3 else '')
        date = 'AD: {}/{}/{} {}'.format(alarm_y % 2000, 
            alarm_m if alarm_m >= 10 else '0{}'.format(alarm_m), 
            alarm_d if alarm_d >= 10 else '0{}'.format(alarm_d),
            '<' if part_changing > 2 else '')
    elif is_setting_time:
        time = 'T: {}:{}:{} {}'.format(temp_hh if temp_hh >= 10 else '0{}'.format(temp_hh), 
            temp_mm if temp_mm >= 10 else '0{}'.format(temp_mm), 
            temp_ss if temp_ss >= 10 else '0{}'.format(temp_ss),
            '<' if part_changing < 3 else '')
        date = 'D: {}/{}/{} {}'.format(temp_y % 2000, 
            temp_m if temp_m >= 10 else '0{}'.format(temp_m), 
            temp_d if temp_d >= 10 else '0{}'.format(temp_d),
            '<' if part_changing > 2 else '')
    else:
        time = 'Time: {}:{}:{}'.format(hh if hh >= 10 else '0{}'.format(hh), 
            mm if mm >= 10 else '0{}'.format(mm), 
            ss if ss >= 10 else '0{}'.format(ss))
        date = 'Date: {}/{}/{}'.format(y % 2000, 
            m if m >= 10 else '0{}'.format(m), 
            d if d >= 10 else '0{}'.format(d))

    # draw time and date on display
    disp.fill(0)
    disp.text(time, 0, 0)
    disp.text(date, 0, 8)

    # draw indicator
    if is_setting_time or is_setting_alarm:
        disp.text('^^', 24 * (part_changing % 3), 16)
    
    # set display contrast with adc readout
    adc_val = adc.read()
    disp.contrast(adc_val if adc_val < 1024 else adc_val - 1)
    disp.show()

    sleep_ms(50)

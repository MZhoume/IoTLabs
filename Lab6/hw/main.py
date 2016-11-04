from machine import RTC
from machine import Pin
from machine import ADC
from machine import PWM
from machine import I2C
from ssd1306 import SSD1306_I2C
from time import sleep_ms
from machine import SPI
import usocket as socket
import ustruct
import gc

global cs, vcc, grnd, spi

# Register constants for the ADXL345 accelerometer
POWER_CTL = const(0x2D)
DATA_FORMAT = const(0x31)
DATAX0 = const(0x32)
DATAX1 = const(0x33)
DATAY0 = const(0x34)
DATAY1 = const(0x35)
DATAZ0 = const(0x36)
DATAZ1 = const(0x37)

# Write to the DATA_FORMAT register to set to 4g.
# Write to POWER_CTL register to begin measurements
def setup():
    writeA(DATA_FORMAT, 0x01)
    writeA(POWER_CTL, 0x08)

# Write command/value to specified register
def writeA(register, value):
    global cs, vcc, grnd, spi

    # Pack register and value into byte format
    write_val = ustruct.pack('B',value)
    write_reg_val = ustruct.pack('B',register)

    # Pull line low and write to accelerometer
    cs.value(0)
    spi.write(write_reg_val)
    spi.write(write_val)
    cs.value(1)

# Read value from a specified register
def readA():
    global cs, vcc, grnd, spi

    # Set the R/W bit high to specify "read" mode
    reg = DATAX0
    reg = 0x80 | reg

    # Set the MB bit high to specify that we want to
    # do multi byte reads.
    reg = reg | 0x40

    # Pack R/W bit + MB bit + register value into byte format
    write_reg_val = ustruct.pack('B',reg)

    # Setup buffers for receiving data from the accelerometer.
    x1 = bytearray(1)
    x2 = bytearray(1)
    y1 = bytearray(1)
    y2 = bytearray(1)
    z1 = bytearray(1)
    z2 = bytearray(1)

    # Read from all 6 accelerometer data registers, one address at a time
    cs.value(0)
    spi.write(write_reg_val)
    spi.readinto(x1)
    spi.readinto(x2)
    spi.readinto(y1)
    spi.readinto(y2)
    spi.readinto(z1)
    spi.readinto(z2)
    cs.value(1)
    
    # Reconstruct the X, Y, Z axis readings from the received data.
    x = (ustruct.unpack('b',x2)[0]<<8) | ustruct.unpack('b',x1)[0]
    y = (ustruct.unpack('b',y2)[0]<<8) | ustruct.unpack('b',y1)[0]
    z = (ustruct.unpack('b',z2)[0]<<8) | ustruct.unpack('b',z1)[0]
    return (x,y,z)

response = '''
HTTP/1.1 200 OK\r\n
%f,%f,%f\r\n
'''

disp_on = False
disp_msg = False
disp_wea = False
disp_time = False
msg = ''
weather = ''
omsg = ''

temp_hh = 0
temp_mm = 0
temp_ss = 0
alarm_hh = 0
alarm_mm = 0
alarm_ss = 0

is_setting_alarm = False
is_setting_time = False
part_changing = -1
has_changed_time = False
is_alarming = False

def btn_a_pressed(p):
    global part_changing
    global has_changed_time
    global is_setting_time
    global is_setting_alarm
    global temp_hh
    global temp_mm
    global temp_ss
    global alarm_hh
    global alarm_mm
    global alarm_ss
    global is_alarming
    global piezo
    global disp

    if is_setting_alarm:
        if part_changing == 0:
            alarm_hh = (alarm_hh +1) % 24
        elif part_changing == 1:
            alarm_mm = (alarm_mm +1) % 60
        elif part_changing == 2:
            alarm_ss = (alarm_ss +1) % 60
    elif is_alarming:
        piezo.duty(0)
        disp.invert(False)
        disp.show()
        is_alarming = False
    else:
        is_setting_time = True
        part_changing = (part_changing + 1) % 6
        if part_changing == 3:
            part_changing = -1
            is_setting_time = False
            has_changed_time = True

def btn_b_pressed(p):
    global part_changing
    global has_changed_time
    global is_setting_alarm
    global is_setting_time
    global temp_hh
    global temp_mm
    global temp_ss
    global alarm_hh
    global alarm_mm
    global alarm_ss
    global is_alarming
    global piezo
    global disp

    if is_setting_time:
        if part_changing == 0:
            temp_hh = (temp_hh +1) % 24
        elif part_changing == 1:
            temp_mm = (temp_mm +1) % 60
        elif part_changing == 2:
            temp_ss = (temp_ss +1) % 60
    elif is_alarming:
        piezo.duty(0)
        disp.invert(False)
        disp.show()
        is_alarming = False
    else:
        is_setting_alarm = True
        part_changing = (part_changing + 1) % 6
        if part_changing == 3:
            part_changing = -1
            is_setting_alarm = False

adc = ADC(0)

cs=Pin(16, Pin.OUT)
spi = SPI(-1, baudrate=500000, polarity=1, phase=1, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
cs.value(0)
cs.value(1)

setup()

piezo = PWM(Pin(15))
piezo.freq(1000)
piezo.duty(0)

rtc = RTC()
rtc.datetime((2016, 1, 1, 0, 0, 0, 0, 0))

disp = SSD1306_I2C(128, 32, I2C(scl=Pin(5), sda=Pin(4), freq=400000))
disp.init_display()

btn_a = Pin(0, Pin.IN, Pin.PULL_UP)
btn_a.irq(trigger=Pin.IRQ_RISING, handler=btn_a_pressed)
btn_b = Pin(2, Pin.IN, Pin.PULL_UP)
btn_b.irq(trigger=Pin.IRQ_RISING, handler=btn_b_pressed)

addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

while True:
    gc.collect()

    print('looping...')
    client_s = s.accept()[0]
    req = client_s.recv(500)
    x, y, z = readA()
    print(x, y, z)
    client_s.send(response % (x, y, z))
    client_s.close()
    gc.collect()

    parts = req.decode('ascii').split(' ')
    if parts[1] == '/turn%20on':
        disp_on = True
    elif parts[1] == '/turn%20off':
        disp_on = False
    elif parts[1] == '/display%20time':
        disp_time = True
    elif parts[1] == '/remove%20time':
        disp_time = False
    elif parts[1] == '/display%20weather':
        disp_wea = True
    elif parts[1] == '/remove%20weather':
        disp_wea = False
    elif parts[1] == '/display%20message':
        disp_msg = True
    elif parts[1] == '/remove%20message':
        disp_msg = False
    elif parts[1] == '/show%20last':
        msg = omsg
    elif parts[1].startswith('/w/'):
        weather = parts[1][3:].replace('%20', ' ')
    elif parts[1].startswith('/t/'):
        omsg = msg
        msg = parts[1][3:].replace('%20', ' ')
    else:
        pass

    if has_changed_time:
        rtc.datetime(((2016, 1, 1, 0, temp_hh, temp_mm, temp_ss, 0)))
        temp_hh = temp_mm = temp_ss = 0
        has_changed_time = False

    disp.fill(0)
    if (not is_alarming) and disp_on:
        if disp_wea:
            disp.text(weather, 0, 16)
        if disp_msg:
            disp.text(msg, 0, 24)
            
        if disp_time:
            y, m, d, t1, hh, mm, ss, t2 = rtc.datetime()
            if not is_setting_alarm and (hh == alarm_hh and mm == alarm_mm and ss == alarm_ss):
                piezo.duty(500)
                disp.invert(True)
                is_alarming = True
            else:
                if is_setting_alarm: 
                    time = 'T: {}:{}:{} {}A'.format(alarm_hh if alarm_hh >= 10 else '0{}'.format(alarm_hh), 
                        alarm_mm if alarm_mm >= 10 else '0{}'.format(alarm_mm), 
                        alarm_ss if alarm_ss >= 10 else '0{}'.format(alarm_ss),
                        '<' if part_changing < 3 else '')
                elif is_setting_time:
                    time = 'T: {}:{}:{} {}'.format(temp_hh if temp_hh >= 10 else '0{}'.format(temp_hh), 
                        temp_mm if temp_mm >= 10 else '0{}'.format(temp_mm), 
                        temp_ss if temp_ss >= 10 else '0{}'.format(temp_ss),
                        '<' if part_changing < 3 else '')
                else:
                    time = 'Time: {}:{}:{}'.format(hh if hh >= 10 else '0{}'.format(hh), 
                        mm if mm >= 10 else '0{}'.format(mm), 
                        ss if ss >= 10 else '0{}'.format(ss))

                disp.text(time, 0, 0)

                if is_setting_time or is_setting_alarm:
                    disp.text('^^', 24 * (part_changing % 3 + 1), 8)
                
        adc_val = adc.read()
        disp.contrast(adc_val if adc_val < 1024 else adc_val - 1)
    disp.show()
import usocket as socket
from machine import Pin
from machine import I2C
from ssd1306 import SSD1306_I2C
from machine import RTC
from time import sleep_ms
from machine import Timer
import gc

disp_on = False
msg = ''

def timer_callback(t):
    global rtc
    global disp
    global disp_on
    y, m, d, t1, hh, mm, ss, t2 = rtc.datetime()
    disp.fill(0)
    if disp_on:
        disp.text('D:{}/{} | T:{}:{}'.format(m, d, mm, ss), 0, 0)
        disp.text(msg, 0, 16)
    disp.show()

response = '''
HTTP/1.1 200 OK\r\n
OK
'''

disp = SSD1306_I2C(128, 32, I2C(scl=Pin(5), sda=Pin(4), freq=400000))
disp.init_display()

rtc = RTC()
rtc.datetime((2016, 1, 1, 0, 0, 0, 0, 0))

tim = Timer(-1)
tim.init(period=1000, mode=Timer.PERIODIC, callback=timer_callback)

addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

while True:
    gc.collect()
    res = s.accept()
    client_s = res[0]
    req = client_s.recv(500)
    client_s.send(response)
    client_s.close()
    parts = req.decode('ascii').split(' ')
    if parts[1] == '/exit':
        break
    elif parts[1] == '/off':
        disp_on = False
    elif parts[1] == '/on':
        disp_on = True
    elif parts[1] == '/favicon.ico':
        pass
    else:
        msg = parts[1][1:]

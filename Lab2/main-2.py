# LED runs on duty from 0 to 200
# Piezo runs on duty from 0 to 10
# ADC output higher when there's light

from time import sleep_ms
from machine import ADC
from machine import Pin
from machine import PWM

# interrupt function
def button_pressed(p):
    global is_working
    isworking = not is_working

# global variable for determine if the program should run
is_working = False

# button was wired to Pin 14
pin_button = Pin(14, Pin.IN, Pin.PULL_UP)

# set the interrupt handler
pin_button.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=button_pressed)

# assign pins for led and piezo
pwm_led = PWM(Pin(12))
pwm_piezo = PWM(Pin(13))

# let's set the frequency to the highest 1000
pwm_led.freq(1000)
pwm_piezo.freq(1000)

# we use ADC 0
adc = ADC(0)

while True:

    # if the program should be working
    while is_working:

        # read the value from ADC
        adc_val = adc.read()

        # calculate the duty value for led and piezo
        led_val = adc_val / 20
        piezo_val = adc_val / 100
        
        # set the duty value
        pwm_led.duty(int(led_val))
        pwm_piezo.duty(int(piezo_val))

        # wait for 50ms till the next sampling
        sleep_ms(50)

    # if the button has been released, the led and piezo should stop working
    pwm_led.duty(0)
    pwm_piezo.duty(0)

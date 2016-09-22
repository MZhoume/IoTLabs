# LED runs on duty from 0 to 200
# Piezo runs on duty from 0 to 10
# ADC output higher when there's light

from time import sleep_ms
from machine import ADC
from machine import Pin
from machine import PWM

# PWM for led outputs from Pin 12
pwm_led = PWM(Pin(12))

# PWM for led outputs from Pin 13
pwm_piezo = PWM(Pin(13))

# let's set the frequency to the highest value
pwm_led.freq(1000)
pwm_piezo.freq(1000)

# we use ADC 0
adc = ADC(0)

while True:

    # read the value from ADC
    adc_val = adc.read()

    # calculate the duty value for led and piezo
    led_val = adc_val / 20
    piezo_val = adc_val / 100

    # set the duty value
    pwm_led.duty(int(led_val))
    pwm_piezo.duty(int(piezo_val))

    # wait for 50ms to sample the next value
    sleep_ms(50)
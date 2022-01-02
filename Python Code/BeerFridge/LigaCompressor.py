import mpu6050
from time import sleep
from math import isclose
import threading
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

compressor = 14
resistor = 15
delay_time = 2


if __name__ == '__main__':
    GPIO.setup(compressor, GPIO.OUT)
    GPIO.setup(resistor, GPIO.OUT)

    GPIO.output(resistor,GPIO.HIGH)
    GPIO.output(compressor,GPIO.LOW)
    #sleep(300)
    #GPIO.output(resistor,GPIO.HIGH)

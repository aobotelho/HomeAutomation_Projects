import mpu6050
from time import sleep
import threading
from BeerFridge import BeerFridge
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

compressor = 14
resistor = 15
delay_time = 2


if __name__ == '__main__':
    GPIO.setup(compressor, GPIO.OUT)
    GPIO.setup(resistor, GPIO.OUT)
    #mpu = mpu6050.mpu6050(0x68)
    beerFridge = BeerFridge()

    while True:
        beerFridge.GetCurrentStates()
        beerFridge.PrintInfo(log=False)
        print('Sleep')
        sleep(delay_time)

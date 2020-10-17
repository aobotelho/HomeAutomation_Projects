import mpu6050
from time import sleep
import threading
from TemperatureController import TemperatureController
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

compressor = 14
resistor = 15
delay_time = 5


if __name__ == '__main__':
    GPIO.setup(compressor, GPIO.OUT)
    GPIO.setup(resistor, GPIO.OUT)
    mpu = mpu6050.mpu6050(0x68)
    beerFridge = TemperatureController(mpu)

    while True:
        beerFridge.GetCurrentStates()
        beerFridge.DefineNextStage()
        beerFridge.PrintInfo()
        sleep(delay_time)
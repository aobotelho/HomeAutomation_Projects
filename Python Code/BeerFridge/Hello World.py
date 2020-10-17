import mpu6050
from time import sleep
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

output1 = 14
output2 = 15
delay_time = 2
if __name__ == '__main__':
    GPIO.setup(output1, GPIO.OUT)
    GPIO.setup(output2, GPIO.OUT)

    while True:
        print('1')
        GPIO.output(output1, GPIO.LOW)
        sleep(delay_time)
        print('2')
        GPIO.output(output2, GPIO.HIGH)
        sleep(delay_time)
        print('3')
        GPIO.output(output1, GPIO.HIGH)
        sleep(delay_time)
        print('4')
        GPIO.output(output2, GPIO.LOW)
        sleep(delay_time)

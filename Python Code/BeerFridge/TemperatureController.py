import RPi.GPIO as GPIO
import mpu6050
from math import isclose
from time import time
from BeerFridge import BeerFridge

class TemperatureController(BeerFridge):
    def __init__(self,
            mpu6050Var: mpu6050,
            targetTempFile: str = './Contoller/targetTemperature.txt',
            deltaTempFile =  './Contoller/deltaTemp.txt',
            currentStateFile = './Contoller/currentState.txt',
            logDataFile = './Contoller/logData.csv',
            OFF = GPIO.HIGH,
            ON = GPIO.LOW,
            WARMING = 'warming',
            COOLING = 'cooling',
            TARGETTEMP = 'targettemp',
            DEFROSTING = 'defrosting',
            compressorPin = 14,
            resistorPin = 15,
            compressorOnTime = 1200,
            defrostingTime = 120):
        self.targetTempFile = targetTempFile
        self.deltaTempFile = deltaTempFile
        self.currentStateFile = currentStateFile
        self.logDataFile = logDataFile
        self.OFF = OFF
        self.ON = ON
        self.WARMING = WARMING
        self.COOLING = COOLING
        self.TARGETTEMP = TARGETTEMP
        self.DEFROSTING = DEFROSTING
        self.compressor = compressorPin
        self.resistor = resistorPin
        self.targetTemp = self.deltaTemp = self.currentTemp = 0
        self.timeCooler = self.timeResistor = 0
        self.currentState = ''
        self.mpu = mpu6050Var
        self.compressorState = self.resistorState = OFF
        self.compressorOnTime = compressorOnTime
        self.defrostingTime = defrostingTime
        self.SetDefaultState()

    
    def DefineNextStage(self):

        if isclose(self.targetTemp,self.currentTemp,abs_tol=0.01):
            self.compressorState = self.OFF
            self.timeCooler = 0
            GPIO.output(self.compressor, self.OFF)
            self.SetCurrentState(self.TARGETTEMP)
        # Current temperature is Higher than target?
        elif self.currentTemp > self.targetTemp:

            if self.currentState == self.WARMING:
                self.compressorState = self.OFF
                GPIO.output(self.compressor, self.OFF)
                self.SetCurrentState(self.TARGETTEMP)

            elif self.currentState == self.COOLING:
                self.compressorState = self.ON

                GPIO.output(self.compressor, self.ON)
                self.SetCurrentState(self.COOLING)

            elif self.currentState == self.TARGETTEMP:
                
                if self.currentTemp >= self.targetTemp + self.deltaTemp:
                    self.compressorState = self.ON
                    GPIO.output(self.compressor, self.ON)
                    self.SetCurrentState(self.COOLING)

                else:
                    self.compressorState = self.OFF
                    GPIO.output(self.compressor, self.OFF)
                    self.SetCurrentState(self.TARGETTEMP)

            else: 
                print('What state is it?!?!')

        # Ok, current temperature is below target temp
        else:
            if self.currentState == self.WARMING:
                self.compressorState = self.OFF
                GPIO.output(self.compressor, self.OFF)
                self.SetCurrentState(self.WARMING)
            elif self.currentState == self.COOLING:
                self.compressorState = self.OFF
                
            elif self.currentState == self.TARGETTEMP:

                if self.currentTemp >= self.targetTemp - self.deltaTemp:
                    self.compressorState = self.OFF
                    GPIO.output(self.compressor, self.OFF)
                    self.SetCurrentState(self.TARGETTEMP)

                else:
                    self.compressorState = self.OFF
                    GPIO.output(self.compressor, self.OFF)
                    self.SetCurrentState(self.WARMING)

            else: 
                print('What state is it?!?!')

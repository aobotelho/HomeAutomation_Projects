import mpu6050
from time import sleep
from math import isclose
import threading
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

compressor = 14
resistor = 15
delay_time = 2


class BeerFridge():    
    def __init__(self,
            mpu6050Var,
            targetTempFile = './Contoller/targetTemperature.txt',
            deltaTempFile =  './Contoller/deltaTemp.txt',
            currentStateFile = './Contoller/currentState.txt',
            OFF = GPIO.HIGH,
            ON = GPIO.LOW,
            WARMING = 'warming',
            COOLING = 'cooling',
            TARGETTEMP = 'targettemp',
            compressorPin = 14,
            resistorPin = 15):
        self.targetTempFile = targetTempFile
        self.deltaTempFile = deltaTempFile
        self.currentStateFile = currentStateFile
        self.OFF = OFF
        self.ON = ON
        self.WARMING = WARMING
        self.COOLING = COOLING
        self.TARGETTEMP = TARGETTEMP
        self.compressor = compressorPin
        self.resistor = resistorPin
        self.targetTemp = self.deltaTemp = self.currentTemp = 0
        self.currentState = ''
        self.mpu = mpu6050Var
        self.compressorState = self.resistorState = OFF
        self.SetDefaultState()

    def GetCurrentStates(self):
        self.currentTemp = self.mpu.get_temp()
        with open(self.targetTempFile,'r') as fin:
            self.targetTemp = float(fin.read())
        with open(self.deltaTempFile,'r') as fin:
            self.deltaTemp = float(fin.read())
        with open(self.currentStateFile,'r') as fin:
            self.currentState = fin.read()

    def SetDefaultState(self):
        self.currentTemp = self.mpu.get_temp()
        with open(self.targetTempFile,'r') as fin:
            self.targetTemp = fin.read()
        with open(self.currentStateFile,'w') as fout:
            self.currState = self.WARMING if float(self.targetTemp) > float(self.currentTemp) else self.COOLING
            fout.write(self.currState)

    def SetCurrentState(self,newState):
        self.currentState = newState
        with open(self.currentStateFile,'w') as fout:
            fout.write(newState)
        
    def DefineNextStage(self):
        if isclose(self.targetTemp,self.currentTemp,abs_tol=0.01):
            self.compressorState = self.OFF
            GPIO.output(self.compressor, self.OFF)
            self.SetCurrentState(self.TARGETTEMP)
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
        else:
            if self.currentState == self.WARMING:
                self.compressorState = self.OFF
                GPIO.output(self.compressor, self.OFF)
                self.SetCurrentState(self.WARMING)
            elif self.currentState == self.COOLING:
                self.compressorState = self.OFF
                GPIO.output(self.compressor, self.OFF)
                self.SetCurrentState(self.TARGETTEMP)
                
                print('ligando resistor')
                GPIO.output(self.resistor, self.ON)
                sleep(30)
                print('DESligando resistor')
                GPIO.output(self.resistor, self.OFF)
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
    
    def PrintInfo(self):
        lineBreak = '\n\t'
        compressorState = 'OFF' if self.compressorState == self.OFF else 'ON'
        print(f'Current stage:{lineBreak} Temp: {round(self.currentTemp,2)}{lineBreak}Target: {self.targetTemp}{lineBreak}Current State: {self.currentState}{lineBreak}Compressor: {compressorState}')

if __name__ == '__main__':
    GPIO.setup(compressor, GPIO.OUT)
    GPIO.setup(resistor, GPIO.OUT)
    mpu = mpu6050.mpu6050(0x68)
    beerFridge = BeerFridge(mpu)
    
    GPIO.output(beerFridge.resistor,beerFridge.ON)
    GPIO.output(beerFridge.compressor,beerFridge.OFF)
    sleep(120)
    GPIO.output(beerFridge.resistor,beerFridge.OFF)

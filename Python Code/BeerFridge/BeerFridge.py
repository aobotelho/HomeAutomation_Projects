import RPi.GPIO as GPIO
import mpu6050
from math import isclose
from time import time,sleep
import glob 

class BeerFridge():    
    def __init__(self,
            mpu6050Var: mpu6050 = None,
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
            compressorOnTime = 900,
            defrostingTime = 500):
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
        self.tempList = []
        self.targetTemp = self.deltaTemp = self.currentTemp = 0
        self.timeCooler = self.timeResistor = 0
        self.currentState = ''
        if mpu6050Var != None:
            self.tempController = mpu6050Var
        else:
            base_dir = '/sys/bus/w1/devices/'
            self.device_folder = glob.glob(base_dir + '28*')[0]
            self.device_file = self.device_folder + '/w1_slave'
            self.tempController = None
        self.compressorState = self.resistorState = OFF
        self.compressorOnTime = compressorOnTime
        self.defrostingTime = defrostingTime
        self.SetDefaultState()

    def GetCurrentStates(self):
        self.SetCurrentTemp()

        with open(self.targetTempFile,'r') as fin:
            self.targetTemp = float(fin.read())
        with open(self.deltaTempFile,'r') as fin:
            self.deltaTemp = float(fin.read())
        with open(self.currentStateFile,'r') as fin:
            self.currentState = fin.read()

    def GetTemp(self):
        if self.tempController:
            return self.tempController.get_temp()
        else:
            def read_temp_raw():
                f = open(self.device_file, 'r')
                lines = f.readlines()
                f.close()
                return lines
            lines = read_temp_raw()
            while lines[0].strip()[-3:] != 'YES':
                sleep(0.2)
                lines = read_temp_raw()
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                return temp_c
    def SetCurrentTemp(self):
        self.tempList.append(self.GetTemp())
        self.tempList = self.tempList[1:]
        print(self.tempList)
        self.currentTemp = round(sum(self.tempList)/len(self.tempList),2)


    def SetDefaultState(self):
        for _ in range(5):
            self.tempList.append(self.GetTemp())
            sleep(1)
            print(self.tempList)
        self.SetCurrentTemp()

        GPIO.output(self.resistor,self.OFF)
        with open(self.targetTempFile,'r') as fin:
            self.targetTemp = fin.read()
        with open(self.currentStateFile,'w') as fout:
            self.currState = self.WARMING if float(self.targetTemp) > float(self.currentTemp) else self.COOLING
            if self.currState == self.WARMING:
                self.timeCooler = time()
            fout.write(self.currState)

    def SetCurrentState(self,newState):
        self.currentState = newState
        with open(self.currentStateFile,'w') as fout:
            fout.write(newState)
        
    def DefineNextStage(self):

        # Am I defrosting?
        if self.currentState == self.DEFROSTING:
            currTime = time()
            if currTime - self.timeResistor >= self.defrostingTime:
                self.resistorState = self.OFF
                self.timeResistor = 0
                self.SetCurrentState(self.COOLING)

        # Is around the target temp?!
        elif isclose(self.targetTemp,self.currentTemp,abs_tol=0.01):
            self.compressorState = self.OFF
            self.timeCooler = 0
            GPIO.output(self.compressor, self.OFF)
            self.SetCurrentState(self.TARGETTEMP)
        # Current temperature is Higher than target tem?
        elif self.currentTemp > self.targetTemp:

            if self.currentState == self.WARMING:
                self.compressorState = self.OFF
                self.timeCooler = 0
                GPIO.output(self.compressor, self.OFF)
                self.SetCurrentState(self.TARGETTEMP)

            elif self.currentState == self.COOLING:
                self.compressorState = self.ON
                currTime = time()

                if self.timeCooler == 0:
                    self.timeCooler = currTime                
                    
                if currTime - self.timeCooler >= self.compressorOnTime:
                    self.compressorState = self.OFF
                    self.SetCurrentState(self.DEFROSTING)
                    self.resistorState = self.ON
                    self.timeResistor = currTime
                    self.timeCooler = 0

                else:
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
                self.SetCurrentState(self.DEFROSTING)
                self.resistorState = self.ON
                self.timeResistor = time()
                self.timeCooler = 0

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
    
    def PrintInfo(self,log=True):
        lineBreak = '\n\t'
        compressorState = 'OFF' if self.compressorState == self.OFF else 'ON'
        resistorState = 'OFF' if self.resistorState == self.OFF else 'ON'
        print(f'Current stage:{lineBreak}Temp: {round(self.currentTemp,2)}{lineBreak}Target: {self.targetTemp}{lineBreak}Current State: {self.currentState}{lineBreak}Compressor: {compressorState}{lineBreak}Resistor: {resistorState}')
        if log:
            with open(self.logDataFile,'a') as fLog:
                fLog.write(f'{round(self.currentTemp,2)},{self.targetTemp},{self.currentState},{compressorState},{resistorState},{time()}\n')

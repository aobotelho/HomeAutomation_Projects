import RPi.GPIO as GPIO
from math import isclose
from time import time,sleep
from w1thermsensor import W1ThermSensor


class BeerFridge():    
    def __init__(self,
            targetTempFile: str = './Contoller/targetTemperature.txt',
            deltaTempFile =  './Contoller/deltaTemp.txt',
            currentStateFile = './Contoller/currentState.txt',
            logDataFile = './Contoller/logData.csv',
            RESISTOR_OFF = GPIO.HIGH,
            RESISTOR_ON = GPIO.LOW,
            COMPRESSOR_OFF = GPIO.LOW,
            COMPRESSOR_ON = GPIO.HIGH,
            WARMING = 'warming',
            COOLING = 'cooling',
            TARGETTEMP = 'targettemp',
            DEFROSTING = 'defrosting',
            compressorPin = 14,
            resistorPin = 15,
            compressorOnTime = 3000,
            defrostingTime = 600):
        self.targetTempFile = targetTempFile
        self.deltaTempFile = deltaTempFile
        self.currentStateFile = currentStateFile
        self.logDataFile = logDataFile
        self.RESISTOR_OFF = RESISTOR_OFF
        self.RESISTOR_ON = RESISTOR_ON
        self.COMPRESSOR_ON = COMPRESSOR_ON
        self.COMPRESSOR_OFF = COMPRESSOR_OFF
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
        self.tempController = W1ThermSensor()
        self.tempControllerType = 'W1'
        self.compressorState = COMPRESSOR_OFF
        self.resistorState = RESISTOR_OFF
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
        return self.tempController.get_temperature()

    def SetCurrentTemp(self):
        self.tempList.append(self.GetTemp())
        self.tempList = self.tempList[1:]
        print(self.tempList)
        self.currentTemp = round(sum(self.tempList)/len(self.tempList),2)


    def SetDefaultState(self):
        for _ in range(5):
            self.tempList.append(self.GetTemp())
            sleep(.1)
            print(self.tempList)
        self.SetCurrentTemp()

        GPIO.output(self.resistor,self.RESISTOR_OFF)
        with open(self.targetTempFile,'r') as fin:
            self.targetTemp = fin.read()
        with open(self.currentStateFile,'w') as fout:
            self.currState = self.WARMING if float(self.targetTemp) > float(self.currentTemp) else self.COOLING
            if self.currState == self.WARMING:
                self.timeCooler = time()
            fout.write(self.currState)
        print(f'Setting first state as {self.currState}')

    def SetCurrentState(self,newState):
        self.currentState = newState
        with open(self.currentStateFile,'w') as fout:
            fout.write(newState)
        
    def DefineNextStage(self):

        # Am I defrosting?
        if self.currentState == self.DEFROSTING:
            currTime = time()
            if currTime - self.timeResistor >= self.defrostingTime:
                self.resistorState = self.RESISTOR_OFF
                GPIO.output(self.resistor,self.RESISTOR_OFF)
                self.timeResistor = 0
                self.SetCurrentState(self.COOLING)

        # Is around the target temp?!
        elif isclose(self.targetTemp,self.currentTemp,abs_tol=0.01):
            self.compressorState = self.COMPRESSOR_OFF
            self.timeCooler = 0
            GPIO.output(self.compressor, self.COMPRESSOR_OFF)
            self.SetCurrentState(self.TARGETTEMP)
        # Current temperature is Higher than target tem?
        elif self.currentTemp > self.targetTemp:

            if self.currentState == self.WARMING:
                self.compressorState = self.COMPRESSOR_OFF
                self.timeCooler = 0
                GPIO.output(self.compressor, self.COMPRESSOR_OFF)
                self.SetCurrentState(self.TARGETTEMP)

            elif self.currentState == self.COOLING:
                self.compressorState = self.COMPRESSOR_ON
                currTime = time()

                if self.timeCooler == 0:
                    self.timeCooler = currTime

                if currTime - self.timeCooler >= self.compressorOnTime:
                    GPIO.output(self.compressor,self.COMPRESSOR_OFF)
                    #self.compressorState = self.OFF
                    self.SetCurrentState(self.DEFROSTING)
                    GPIO.output(self.resistor,self.RESISTOR_ON)
                    self.resistorState = self.RESISTOR_ON
                    self.timeResistor = currTime
                    self.timeCooler = 0

                else:
                    GPIO.output(self.compressor, self.COMPRESSOR_ON)
                    self.SetCurrentState(self.COOLING)

            elif self.currentState == self.TARGETTEMP:

                if self.currentTemp >= self.targetTemp + self.deltaTemp:
                    self.compressorState = self.COMPRESSOR_ON
                    GPIO.output(self.compressor, self.COMPRESSOR_ON)
                    self.SetCurrentState(self.COOLING)

                else:
                    self.compressorState = self.COMPRESSOR_OFF
                    GPIO.output(self.compressor, self.COMPRESSOR_OFF)
                    self.SetCurrentState(self.TARGETTEMP)

            else: 
                print('What state is it?!?!')

        # Ok, current temperature is below target temp
        else:
            if self.currentState == self.WARMING:
                self.compressorState = self.COMPRESSOR_OFF
                GPIO.output(self.compressor, self.COMPRESSOR_OFF)
                self.SetCurrentState(self.WARMING)
            elif self.currentState == self.COOLING:
                self.compressorState = self.COMPRESSOR_OFF
                self.SetCurrentState(self.WARMING)
                self.resistorState = self.RESISTOR_OFF
                self.timeResistor = time()
                self.timeCooler = 0

            elif self.currentState == self.TARGETTEMP:

                if self.currentTemp >= self.targetTemp - self.deltaTemp:
                    self.compressorState = self.COMPRESSOR_OFF
                    GPIO.output(self.compressor, self.COMPRESSOR_OFF)
                    self.SetCurrentState(self.TARGETTEMP)

                else:
                    self.compressorState = self.OFF
                    GPIO.output(self.compressor, self.COMPRESSOR_OFF)
                    self.SetCurrentState(self.WARMING)

            else: 
                print('What state is it?!?!')
    
    def PrintInfo(self,log=True):
        lineBreak = '\n\t'
        compressorState = 'OFF' if self.compressorState == self.COMPRESSOR_OFF else 'ON'
        resistorState = 'OFF' if self.resistorState == self.RESISTOR_OFF else 'ON'
        print(f'Current stage:{lineBreak}Temp: {round(self.currentTemp,2)}{lineBreak}Target: {self.targetTemp}{lineBreak}Current State: {self.currentState}{lineBreak}Compressor: {compressorState}{lineBreak}Resistor: {resistorState}')
        if log:
            with open(self.logDataFile,'a') as fLog:
                fLog.write(f'{round(self.currentTemp,2)},{self.targetTemp},{self.currentState},{compressorState},{resistorState},{time()}\n')

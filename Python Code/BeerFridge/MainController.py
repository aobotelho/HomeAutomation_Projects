from time import sleep
import threading
from BeerFridge import BeerFridge
from BeerFridgeUI.BeerFridgeUI import BeerFridgeUI
import RPi.GPIO as GPIO
import PySimpleGUI as sg

GPIO.setmode(GPIO.BCM)

compressor = 14
resistor = 15
delay_time = 1


if __name__ == '__main__':
    GPIO.setup(compressor, GPIO.OUT)
    GPIO.setup(resistor, GPIO.OUT)

    beerFridge = BeerFridge()
    ui = BeerFridgeUI()

    while True:
        try:
            beerFridge.GetCurrentStates()
            beerFridge.DefineNextStage()

            ui.UpdateParameters()

            if ui.event == 'OK' or ui.event == sg.WIN_CLOSED:
                break

            elif ui.event == ui.key_down_button:
                print('Encontrei DOWN')
                ui.DownButton(beerFridge.targetTempFile)
            elif ui.event == ui.key_up_button:
                print('Encontrei UP')
                ui.UpButton(beerFridge.targetTempFile)
            else:
                try:
                    print(f'Encontrei {ui.event}')
                    ui.functions_dict(ui.event)()
                except Exception as e:
                    print(f'Error on trying to act on event. Event: {ui.event}')
                    print(e)

            beerFridge.PrintInfo()
            ui.UpdateDateTime()
            ui.UpdateCurrentState(round(beerFridge.currentTemp,2),beerFridge.currentState)
            sleep(delay_time)
        except Exception as e:
            print('Deu Erro!!!!')
            print(e)

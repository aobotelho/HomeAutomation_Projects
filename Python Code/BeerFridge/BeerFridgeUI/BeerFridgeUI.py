import PySimpleGUI as sg
from PIL import Image, ImageDraw
from math import floor
from datetime import datetime
from time import sleep

from PySimpleGUI.PySimpleGUI import DummyButton

class BeerFridgeUI():
    def __init__(self
            ,resize_factor: int = 20
            ,figure_size: tuple = (32,9)
            ,column_logo_size: tuple = (3,9)
            ,column_2_size: tuple = (27,9)
            ,column_2_date_size:tuple = (6,4)
            ,current_state_logo_size:tuple = (2,4)
            ,current_state_text_size:tuple = (7,4)
            ,target_logo_size:tuple = (2,4)
            ,target_text_size:tuple = (4,4)
            ,target_up_arrow_size:tuple = (3,4)
            ,target_down_arrow_size:tuple = (3,4)
            ,graph_size:tuple = (27,5)
        ):

        self.resize_factor: int = resize_factor
        self.figure_size = tuple((i * resize_factor for i in figure_size))
        self.column_logo_size = tuple((i * resize_factor for i in column_logo_size))
        self.column_2_size = tuple((i * resize_factor for i in column_2_size))
        self.column_2_date_size = tuple((i * resize_factor for i in column_2_date_size))
        self.current_state_logo_size = tuple((i * resize_factor for i in current_state_logo_size))
        self.current_state_text_size = tuple((i * resize_factor for i in current_state_text_size))
        self.target_logo_size = tuple((i * resize_factor for i in target_logo_size))
        self.target_text_size = tuple((i * resize_factor for i in target_text_size))
        self.target_up_arrow_size = tuple((i * resize_factor for i in target_up_arrow_size))
        self.target_down_arrow_size = tuple((i * resize_factor for i in target_down_arrow_size))
        self.graph_size = tuple((i * resize_factor for i in graph_size))

        #Prepping images 
        # Logo
        self.ResizeImage('./BeerFridgeUI/images/logo.png',self.column_logo_size,keep_ratio=True, fill_bottom = True)
        # Graph
        self.ResizeImage('./BeerFridgeUI/images/mockup_graph.png',self.graph_size,keep_ratio=True, fill_bottom = True)
        #Thermometer Blue
        self.ResizeImage('./BeerFridgeUI/images/thermometer_blue.png',self.current_state_logo_size,keep_ratio=True, fill_bottom = False)
        #Thermometer White
        self.ResizeImage('./BeerFridgeUI/images/thermometer_white.png',self.target_logo_size,keep_ratio=True, fill_bottom = False)
        #Green Up Arrow
        self.ResizeImage('./BeerFridgeUI/images/green_arrow_button.png',self.target_up_arrow_size,keep_ratio=True, fill_bottom = True)
        #Red Down Arros
        self.ResizeImage('./BeerFridgeUI/images/red_arrow_button.png',self.target_down_arrow_size,keep_ratio=True, fill_bottom = True)

        self.key_logo_image_key = '-logo_image-'
        self.key_current_datetime = '-current_datetime-'
        self.key_current_state_logo = '-current_state_logo-'
        self.key_current_state_text = '-current_state_text-'
        self.key_target_logo = '-target_logo-'
        self.key_target_temp = '-target_temp-'
        self.key_down_button = '-down_button-'
        self.key_up_button = '-up_button-'

        self.functions_dict = {
            self.key_logo_image_key: self.DummyFunction
            ,self.key_current_datetime: self.CurrentDatetimeFormat
            ,self.key_current_state_logo: self.DummyFunction
            ,self.key_current_state_text: self.CurrentStateFormat
            ,self.key_target_logo: self.DummyFunction
            ,self.key_target_temp: self.FormatTemperature
            ,self.key_down_button: self.DownButton
            ,self.key_up_button: self.UpButton
        }

        column_logo = [[
            sg.Image('./BeerFridgeUI/images/logo_resized.png',size=self.column_logo_size,pad = 0, key = self.key_logo_image_key)
        ]]

        column_2 = [[
                sg.Column([[
                    sg.Text(
                        self.CurrentDatetimeFormat()
                        ,size=self.column_2_date_size
                        ,auto_size_text=True
                        ,text_color='#00FF00'
                        ,font=("Helvetica", int(round(self.resize_factor/2,0)))
                        ,justification='left'
                        ,pad = 0
                        ,background_color='black'
                        ,key = self.key_current_datetime)
                    ]]
                    ,size = self.column_2_date_size
                    ,pad =0
                    ,background_color = 'black'
                )
                ,sg.Column([[
                    sg.Image(
                        './BeerFridgeUI/images/thermometer_blue_resized.png'
                        ,size=self.current_state_logo_size
                        ,pad = 0
                        ,background_color = 'black'
                        ,key = self.key_current_state_logo
                    )
                    ]]
                    ,size=self.current_state_logo_size
                    ,pad=0
                    ,background_color = 'black'
                )
                ,sg.Column([[
                    sg.Text(
                        self.CurrentStateFormat(123,'cooling')
                        ,size = self.current_state_text_size
                        ,auto_size_text = True
                        ,text_color = '#A4D0FB'
                        ,font = ("Helvetica", int(round(self.resize_factor*1.25,0)))
                        # ,justification='top'
                        ,pad = 0
                        ,background_color = 'black'
                        ,key = self.key_current_state_text
                    )
                    ]]
                    ,size = self.current_state_text_size
                    ,pad = 0
                    ,background_color = 'black'
                )
                ,sg.Column([[
                    sg.Image(
                        './BeerFridgeUI/images/thermometer_white_resized.png'
                        ,size = self.target_logo_size
                        ,pad = 0
                        ,key = self.key_target_logo
                        ,background_color = 'black'
                    )
                    ]]
                    ,size = self.target_logo_size
                    ,pad = 0
                    ,background_color = 'black'
                )
                ,sg.Column([[
                    sg.Text(
                        self.FormatTemperature(69)
                        ,size = self.target_text_size
                        ,auto_size_text = True
                        ,text_color = '#00FF00'
                        ,font = ("Helvetica", int(round(self.resize_factor*1.25,0)))
                        # ,justification='top'
                        ,pad = 0
                        ,background_color = 'black'
                        ,key = self.key_target_temp
                    )
                    ]]
                    ,size = self.target_text_size
                    ,pad = 0
                    ,background_color = 'black'
                )
                ,sg.Image(
                    './BeerFridgeUI/images/red_arrow_button_resized.png'
                    ,size = self.target_down_arrow_size
                    ,pad = 0
                    ,background_color = 'black'
                    ,enable_events = True
                    ,key = self.key_down_button
                )
                ,sg.Image(
                    './BeerFridgeUI/images/green_arrow_button_resized.png'
                    ,size = self.target_up_arrow_size
                    ,pad = 0
                    ,background_color = 'black'
                    ,enable_events = True
                    ,key = self.key_up_button
                )
            ]
            ,[sg.Image('./BeerFridgeUI/images/mockup_graph_resized.png',size = self.graph_size, pad = 0, background_color = 'yellow')]
        ]
        
        layout = [[
            sg.Column(column_logo, size = self.column_logo_size, pad = 0, background_color = 'black')
            ,sg.Column(column_2, size = self.column_2_size, pad = 0, background_color = 'black')
        ]]

        self.window = sg.Window(
            'Teste'
            ,layout
            ,size=self.figure_size
            ,background_color='black'
        )
        
        self.event = None
        self.values = None

        pass
    
    def DummyFunction(self):
        pass

    def UpdateParameters(self):
        self.event, self.values = self.window.read()
        pass

    def FormatTemperature(self,current_temp):
        _DEGREE_SIGN = u'\N{DEGREE SIGN}'
        return f"{current_temp}{_DEGREE_SIGN}"

    def CurrentStateFormat(self,current_temperature:float,current_state: str):
        return f'{self.FormatTemperature(current_temperature)}\n{current_state}'

    def CurrentDatetimeFormat(self):
        return f'{datetime.now().strftime("%m/%d/%Y %H:%M")}'

    def UpdateDateTime(self):
        self.window[self.key_current_datetime].update(f'Andre Botelho\nBeer Fridge Automation\n{self.CurrentDatetimeFormat()}')
    
    def UpdateTargetTemp(self,target_temp):
        self.window[self.key_target_temp].update(self.FormatTemperature(target_temp))
        pass

    def UpdateCurrentState(self,current_temp, state_text):
        self.window[self.key_current_state_text].update(self.CurrentStateFormat(current_temp,state_text))
        pass
    
    def UpButton(self, file_path:str):
        with open(file_path,'r') as fin:
            targetTemp = float(fin.read())
        
        targetTemp = targetTemp + 0.1

        with open(file_path,'w') as fout:
            fout.write(targetTemp)
        
        self.UpdateTargetTemp(targetTemp)
        pass

    def DownButton(self,file_path:str):
        with open(file_path,'r') as fin:
            targetTemp = float(fin.read())
        
        targetTemp = targetTemp - 0.1

        with open(file_path,'w') as fout:
            fout.write(targetTemp)
        
        self.UpdateTargetTemp(targetTemp)
        pass

    def ResizeImage(self,image_path,new_size, keep_ratio = False, fill_bottom = False):
        im = Image.open(image_path)
        if keep_ratio:
            tuple_resize_factor = tuple((el1/el2 for el1,el2 in zip(new_size,im.size)))
            
            resize_factor = min(tuple_resize_factor)
            
            new_size_adjusted = tuple((floor(resize_factor * i) for i in im.size))
            
            im = im.resize(new_size_adjusted)
        else:
            im = im.resize(new_size)
        
        if fill_bottom:
            missing_space = new_size[1] - im.size[1]
            if missing_space > 0:
                im2 = Image.new(im.mode,size = (im.size[0], im.size[1] + missing_space),color=(0,0,0))
                im2.putdata(im.getdata())

                im = im2
        im.save(image_path.split('.png')[0] + '_resized.png')
        return im

    def CloseWindow(self):
        self.window.close()
        pass

if __name__ == '__main__':
    ui = BeerFridgeUI()

    while True:
        ui.UpdateParameters()
        if ui.event == 'OK' or ui.event == sg.WIN_CLOSED:
            break
        #sleep(1)
    
    ui.CloseWindow()

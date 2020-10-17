import terminalplot as tpl


if __name__ == '__main__':
    while True:
        with open('./Contoller/logData.csv','r') as fin:
            dataLines = fin.readlines()[-20:]
        
        x = [dataLines.index(element) for element in dataLines]
        y = [float(x.split(',')[0]) for x in dataLines]
        
        tpl.plot(x, y)

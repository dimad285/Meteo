import socket
import struct
from typing import Union
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib import ticker
from matplotlib.widgets import CheckButtons
from datetime import date
from datetime import datetime
from datetime import time
import time as tm
import os
from tkinter import filedialog as fd

plot_date = date.today().strftime("%d-%m-%Y")

norm_coef = (22, 40, 750, 500, 1000, 25)
color_palet = {'grey': (0.15, 0.15, 0.15)}
var_names = ("TEMPERATURE", "HUMIDITY", "PRESSURE:", "VOC", "CO2", "PM2.5:")


class data_arr:

    ''' data structure: 0 - temperature, 1 - humidity, 2 - pressure, 3 - voc, 4 - co2, 5 - pm '''

    def __init__(self) -> None:
        self.minutes: int = 0
        self.temperature: list[float] = []
        self.humidity: list[float] = []
        self.pressure: list[float] = []
        self.voc: list[float] = []
        self.co2: list[float] = []
        self.pm: list[float] = []
        self.data: list[list[float]] = [self.temperature, self.humidity,
                                        self.pressure, self.voc, self.co2, self.pm]

    def empty(self, start = 0, end = 6):
        for i in range(start, end):
            del self.data[i][:]

    def data_wrap(self, input: list[float], norm_coef: tuple = (1,)*6) -> None:
        '''
        puts 'input' list with minutes*6 lenght in two-dimentional list 'output'
        '''
        self.empty()
        for j in range(self.minutes):
            for k in range(6):
                self.data[k].append(input[j*6 + k]/norm_coef[k])


def send(com: str, IP: str, port: int) -> None:

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((IP, port))
    except(socket.error):
        print('Connection Error')
    else:
        try:
            s.send(len(com).to_bytes(1, 'big'))
        except(socket.error):
            print("Couldn't send data size")
        else:
            try:
                s.send(bytes(com, encoding='utf-8'))
            except:
                print("Couldn't send data")
            else:
                print("Data has been sent")
        finally:
            try:
                s.close()
            except:
                print('Couldnt close socket')


def receive(IP: str, port: int, buffer: list[bytes] = None) -> Union[int, list[float]]:
    '''
    Returns minutes list of float valuse received from server
    '''

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_b:list[bytes] = []
    data_f = []
    minutes = 1

    try:
        print('Connecting')
        s.connect((IP, port))
    except:
        print('Connection Error')
    else:
        print('Connected to the server')
        try:
            s.send(len('receive').to_bytes(1, 'big'))
        except:
            print("Couldn't send data size")
        else:
            try:
                s.send(bytes('receive', encoding='utf-8'))
            except:
                print("Couldn't receive data")
            else:
                try:
                    k = 0
                    while (True):
                        data_r = s.recv(2048)
                        if data_r == -1:
                            break
                        k += 1
                        for i in data_r:
                            data_b.append(i)                                    
                        print(len(data_b), "     ", round(
                            len(data_b)/69122*100, 2), "%", end='     ')  # will be more then 100%
                        print('|', end='')
                        for i in range(0, k):
                            print('█', end='')
                        for i in range(0, 50-k):
                            print(' ', end='')
                        print('|',end='\r')
                        if k>100:        
                            print(''.join(map(chr, data_b)))
                            break
                    s.close()                    
                except:
                    print('\n' + "Couldn't receive data")
                else:
                    print('\n' + "Data received")
                    
    finally:
        s.close()
        print('Socket has been closed')

    minutes = sum(struct.unpack('H', bytearray(data_b[:2])))
    plot_date = date.today().strftime("%d-%m-%Y")

    print("minutes = ", minutes)

    byte_to_float(data_b, data_f)

    file_w_raw(data_b,os.getcwd() + '\\data_byte\\' + plot_date + '.data')

    return minutes, data_f

def byte_to_float(data_b, data_f, offset = 2):
    k = 0
    buff = [0]*4

    for i in data_b[offset:]:
        buff[k] = i
        k += 1
        if (k == 4):
            k = 0
            tmp = ''.join(map(str, struct.unpack('f', bytearray(buff))))
            data_f.append(float(tmp))


def plot_time(minutes: int) -> list[str]:
    t_cur = datetime.now().strftime(format="%H:%M")
    t_curh = int(t_cur.split(':')[0])
    t_curm = int(t_cur.split(':')[1])
    t_plot = [0]*minutes
    t_min = t_curh * 60 + t_curm  # Current time in minutes
    for i in range(0, minutes):
        h = (t_min - i)//60
        m = t_min - i - h*60
        t_plot[minutes - i - 1] = time(h, m).strftime("%H:%M")

    return t_plot


def plot(fig, data: data_arr, canvas=None):
    fig.clf()
    time = plot_time(data.minutes)
    ax = fig.add_subplot(111)
    ax.set_facecolor(color_palet['grey'])
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(colors='white')
    ax.grid(True)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(60.00))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(10.00))
    ax.set_xlim(0, data.minutes)
    temp, = ax.plot(time, data.temperature, 'r')
    hum, = ax.plot(time, data.humidity, 'c')
    pres, = ax.plot(time, data.pressure, '--')
    voc, = ax.plot(time, data.voc, 'g')
    co2, = ax.plot(time, data.co2, 'y')
    pm, = ax.plot(time, data.pm, 'b')
    fig.legend([temp, hum, pres, co2, voc, pm],
               ['Temperature (°C)', 'humidity (%)', 'pressure (mm)', 'CO2 (ppm)', 'VOC (ppb)', 'PM2.5 (ug/m³)'])
    fig.text(0.15, 0.8, plot_date, color='white')
    if canvas == None:
        plt.show()
    else:
        canvas.draw()


def file_w(data: data_arr, path: str):
    f = open(path, 'w')
    f.write("TIME:" + datetime.now().strftime(format="%H:%M") + "\n")
    f.write("MINUTES:" + str(data.minutes) + "\n")
    for k in range(6):
        f.write(var_names[k] + "\n")
        for i in data.data[k]:
            f.write(str(i) + "\n")
    f.close()


def file_r(minutes: int, in_arr: data_arr):

    in_arr.empty()
    file_name = fd.askopenfilename()
    global plot_date
    #plot_date = str(file_name) - str(os.getcwd()) - '\\data\\' - '.txt'
    global t_cur
    t_cur = tm.ctime(os.path.getmtime(filename=file_name)
                     )  # returns day month time year
    t_cur = t_cur[11:16]
    print("Opend: " + file_name)
    print('date: ', plot_date, '  time: ', t_cur[:])
    f = open(file_name, 'r')
    while True:
        t = f.readline()

        if t == '':
            break

        if "MINUTES" in t:
            minutes = int(t.split(':')[1])
            print(minutes)
            t = f.readline()

        if "TEMPERATURE" in t:
            i = 0
            while i < minutes:
                t = f.readline()
                in_arr.temperature.append(float(t))
                i += 1

        if "HUMIDITY" in t:
            i = 0
            while i < minutes:
                t = f.readline()
                in_arr.humidity.append(float(t))
                i += 1

        if "PRESSURE" in t:
            i = 0
            while i < minutes:
                t = f.readline()
                in_arr.pressure.append(float(t))
                i += 1

        if "CO2" in t:
            i = 0
            while i < minutes:
                t = f.readline()
                in_arr.co2.append(float(t))
                i += 1

        if "VOC" in t:
            i = 0
            while i < minutes:
                t = f.readline()
                in_arr.voc.append(float(t))
                i += 1

        if "PM" in t:
            i = 0
            while i < minutes:
                t = f.readline()
                in_arr.pm.append(float(t))
                i += 1

    f.close()


def file_w_raw(input: list[bytes], path: str) -> None:
    f = open(path, 'w')
    f.write(str(input))
    f.close()

def file_r_raw(input: list[float]) -> None:
    pass


def dif():
    pass

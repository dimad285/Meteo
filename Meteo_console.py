import tkinter as tk
import tkinter.font as font
import tkinter.ttk as ttk
from ttkthemes import ThemedStyle
from ttkthemes import ThemedTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import os
import sys
import modules.meteosoc as msoc


IP = "192.168.1.46"
port = 123


class Window:

    def __init__(self, master) -> None:
        self.master = master


data_nom = msoc.data_arr()  # give better name
data_norm = msoc.data_arr()
#data_f = []


def get_data(nom=data_nom, norm=data_norm):
    minutes = 0
    minutes, data_f = msoc.receive(IP, port)
    nom.minutes = norm.minutes = minutes
    nom.data_wrap(data_f)
    norm.data_wrap(data_f, msoc.norm_coef)
    msoc.file_w(nom, os.getcwd() + '\\data\\' + msoc.plot_date + '.txt')


def win_set(win):

    win_width = "1280"
    win_height = "720"
    win.resizable(0, 0)
    win.title('Meteo')
    win.geometry(win_width + "x" + win_height)
    win.configure(background='gray20')
    win.config(highlightbackground="gray20")
    style = ThemedStyle(win)
    style.set_theme("equilux")
    win.iconbitmap(os.getcwd() + '\\assets\\wpweather.ico')
    font1 = font.Font(size=15)

    fig = plt.figure(figsize=(10, 10), dpi=100)
    fig.patch.set_facecolor(msoc.color_palet['grey'])
    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.Y)
    toolbar = NavigationToolbar2Tk(canvas, win)  # define canvas properly
    toolbar.update()

    btn1 = tk.Button(win, text='receive', width=20,
                     bg='#4f4f4f', fg='#ffffff', font=font1, bd=1)
    btn2 = tk.Button(win, text='plot nominal', width=20,
                     bg='#4f4f4f', fg='#ffffff', font=font1, bd=1)
    btn3 = tk.Button(win, text='plot normalized', width=20,
                     bg='#4f4f4f', fg='#ffffff', font=font1, bd=1)
    btn4 = tk.Button(win, text='open file', width=20,
                     bg='#4f4f4f', fg='#ffffff', font=font1, bd=1)

    lbl1 = tk.Label(win, bg='#4f4f4f', fg='#ffffff')
    lbl2 = tk.Label(win, bg='#4f4f4f', fg='#ffffff')

    btn1.bind("<Button-1>", lambda event: get_data())
    btn2.bind("<Button-1>", lambda event: msoc.plot(
              fig, data_nom, canvas))
    btn3.bind("<Button-1>", lambda eebent: msoc.plot(
              fig, data_norm, canvas))
    #btn4.bind("<Button-1>",lambda event: msoc.file_r(data_nom))

    btn1.pack()
    btn2.pack()
    btn3.pack()
    btn4.pack()
    lbl1.pack()
    lbl2.pack()


def UI():
    window = ThemedTk()
    win_set(window)
    window.mainloop()


command_set = ['receive', 'plot_nominal', 'plot_normalized', 'quit', 'help', 'print_nominal', 'print_normalized',
               'bufferf', 'clear', 'data_wrap', 'data_normalize', 'save_path', 'set_save_path', 'save_file', 'load_file', 'send', 'start']


def console():

    while True:
        command = input('type command\n')
        if command == command_set[0]:
            data_nom = data_norm, data_plot = msoc.receive("192.168.1.46", 123)
        elif command == command_set[1]:
            fig_1 = plt.figure(
                figsize=(12, 7), facecolor=msoc.color_palet['grey'])
            msoc.plot(fig_1, data_nom)
        elif command == command_set[2]:
            fig_2 = plt.figure(
                figsize=(12, 7), facecolor=msoc.color_palet['grey'])
            msoc.plot(fig_2, data_norm)
        elif command == command_set[3]:
            sys.exit()
        elif command == command_set[4]:
            print(command_set)
        elif command == command_set[5]:
            print(data_nom.data)
        elif command == command_set[6]:
            print(data_norm.data)
        elif command == command_set[7]:
            print(data_plot)
        elif command == command_set[8]:
            os.system('cls')
        elif command == command_set[9]:
            data_nom.data_wrap(data_plot)
        elif command == command_set[10]:
            pass
            #msoc.data_wrap(data_plot, data_norm, minutes, msoc.norm_coef)
        elif command == command_set[13]:
            msoc.file_w(data_nom, path=os.getcwd()+"\\data\\" +
                        str(msoc.plot_date) + '.txt')
        elif command == command_set[14]:
            msoc.file_r(data_nom)
        elif command_set[15] in command:
            com = command[command.find('(')+1:command.find(')')]
            msoc.send(com, IP, port)
        elif command == command_set[16]:
            UI()
        else:
            print("wrong command")

console()


#UI()

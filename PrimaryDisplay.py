#!/usr/env/python3

import RPi.GPIO as GPIO
import collections
import json
import socket
from tkinter import *
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import queue
import Server
import Checkbar
import PumpThread
import Commands


def heatIndexCalc(T, RH):
    if T <= 80:
        return 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (RH * 0.094))
    else:
        return -42.379 + 2.04901523 * T + 10.14333127 * RH - .22475541 * T * RH - \
               .00683783 * T * T - .05481717 * RH * RH + .00122874 * T * T * RH + \
               .00085282 * T * RH * RH - .00000199 * T * T * RH * RH


PATH = os.path.dirname(os.path.realpath(__file__))
dataQueue = queue.Queue()
MAX_DATA_POINTS = 25
sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recvSocket.bind(("0.0.0.0", 6556))
failedAttempts = 0
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

dataLines = collections.deque(maxlen=MAX_DATA_POINTS)
client_Addr = ('192.168.1.247', 6557)

window = Tk()
window.title("Greenhouse Controller")
window.resizable(True, True)

settings = {}
if os.path.exists(PATH + '\\settings.json'):
    with open(PATH + '\\settings.json', 'r') as jFile:
        settings = json.load(jFile)
else:
    settings['pump1Runtime'] = 30
    settings['pump2Runtime'] = 30
    settings['DOTW'] = [0, 0, 0, 0, 0, 0, 0]
    settings['runTimeH'] = '12'
    settings['runTimeM'] = '00'

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_ylim(ymin=0, ymax=100)
ax.set_xlim(xmin=0, xmax=25)
ax.set_xlabel('Time Step')
ax.set_ylabel('Temp (°F) / Relative Humidity (%)')
line1, = ax.plot(np.arange(25), [0] * 25, label="Temperature")
line2, = ax.plot(np.arange(25), [0] * 25, label="Humidity")
line3, = ax.plot(np.arange(25), [0] * 25, label="Heat Index")
fig.legend()

labels = LabelFrame(window, text='Greenhouse Status', padx=10, pady=10)
labels.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky=E + W + N + S)

buttons = Frame(window, padx=10, pady=10)
buttons.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky=E + W + N + S)

graph = FigureCanvasTkAgg(fig, master=window)


def shutdownCheck():
    if GPIO.input(10) == GPIO.HIGH:
        os.system("sudo shutdown -h now")

def processQueue():
    global failedAttempts
    if failedAttempts > 250:
        connStatusLabel.config(text="Down", foreground='red')
    try:
        msg = dataQueue.get_nowait()
        failedAttempts = 0
        connStatusLabel.config(text="Up", foreground='green')
        if 'nan' not in msg:
            msg = msg.split(',')
            dataLines.append((round(float(msg[0]), 3), round(float(msg[1]), 3)))
            updateGraph()
        window.after(100, processQueue)
    except queue.Empty:
        failedAttempts += 1
        window.after(100, processQueue)


def updateGraph():
    global dataLines
    temp_axis = [round(float(line[1])) for line in dataLines]
    humid_axis = [round(float(line[0])) for line in dataLines]
    line1.set_data(np.arange(len(temp_axis)), temp_axis)
    line2.set_data(np.arange(len(humid_axis)), humid_axis)
    line3.set_data(np.arange(len(humid_axis)),
                   [heatIndexCalc(temp_axis[x], humid_axis[x]) for x in range(len(temp_axis))])
    graph.draw()



def updateTime():
    dateTimeLabel.config(text=f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
    labels.after(500, updateTime)


def pad(value):
    if int(value) < 10:
        return f"0{int(value)}"
    return value


def validateTime(h, m):
    try:
        h = int(h)
    except TypeError or ValueError:
        return False
    if not 0 <= h < 24:
        return False
    try:
        m = int(m)
    except TypeError or ValueError:
        return False
    if not 0 <= m < 60:
        return False
    return True


def saveSettings(field1, field2, field3, field4, field5, frame):
    global settings, pump, cmds
    if validateTime(field4.get(), field5.get()):
        settings['pump1Runtime'] = field1.get()
        settings['pump2Runtime'] = field2.get()
        settings['DOTW'] = field3.state()
        settings['runTimeH'] = pad(field4.get())
        settings['runTimeM'] = pad(field5.get())
        with open(f"{PATH}\\settings.json", 'w') as jFile:
            json.dump(settings, jFile)
        pump.killThread()
        pump.join()
        cmds.updateSettings(settings)
        pump = PumpThread.pumpThread(sendSocket=sendSocket, settings=settings, cmds=cmds)
        pump.start()
        frame.destroy()


def settingsMenu():
    global settings
    settingsFrame = Toplevel(window)
    settingsFrame.title("Settings")
    frame1 = Frame(master=settingsFrame)
    frame2 = Frame(master=settingsFrame)
    frame3 = Frame(master=settingsFrame)
    frame4 = Frame(master=settingsFrame)
    frame5 = Frame(master=settingsFrame)
    frame6 = Frame(master=settingsFrame)
    frame7 = Frame(master=settingsFrame)
    frame1.pack(side='top', fill='both', expand=True)
    frame2.pack(side='top', fill='both', expand=True)
    frame3.pack(side='top', fill='both', expand=True)
    frame4.pack(side='top', fill='both', expand=True)
    frame6.pack(side='top', fill='both', expand=True)
    frame7.pack(side='top', fill='both', expand=True)
    frame5.pack(side='top', fill='both', expand=True)
    l1 = Label(master=frame1, text="Pump 1 Runtime")
    l2 = Label(master=frame3, text="Pump 2 Runtime")
    l3 = Label(master=frame7, text="Run at time")
    l4 = Label(master=frame7, text=':')
    p1Run = Entry(master=frame2, justify='center')
    p1Run.insert(0, settings['pump1Runtime'])
    p2Run = Entry(master=frame4, justify='center')
    p2Run.insert(0, settings['pump2Runtime'])
    rt1 = Entry(master=frame7, justify='center')
    rt1.insert(0, settings['runTimeH'])
    rt2 = Entry(master=frame7, justify='center')
    rt2.insert(0, settings['runTimeM'])
    checkBoxes = Checkbar.Checkbar(frame6, picks=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                                   values=settings['DOTW'])
    b1 = Button(master=frame5, text='Save Settings',
                command=lambda: saveSettings(p1Run, p2Run, checkBoxes, rt1, rt2, settingsFrame))

    l1.grid(row=0, column=0)
    l2.grid(row=1, column=0)
    l3.grid(row=2, column=0)
    l4.grid(row=2, column=2)
    p1Run.grid(row=0, column=1)
    p2Run.grid(row=1, column=1)
    rt1.grid(row=2, column=1)
    rt2.grid(row=2, column=3)
    checkBoxes.grid(row=3, column=0)
    b1.grid(row=4, column=0)



dateTimeLabel = Label(master=labels, text=f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}", foreground="black")
lastRunLabel = Label(master=labels, text="Last Run ", foreground="black")
lastRunTimeLabel = Label(master=labels, text="No Data", foreground="red")
connLabel = Label(master=labels, text="Server Status ", foreground="black")
connStatusLabel = Label(master=labels, text="Down", foreground="red")
pump1Label = Label(master=labels, text="Pump 1 Status ", foreground="black")
pump2Label = Label(master=labels, text="Pump 2 Status ", foreground="black")
pump1StatusLabel = Label(master=labels, text="Off", foreground="red")
pump2StatusLabel = Label(master=labels, text="Off", foreground="red")
cmds = Commands.Commands(pump1StatusLabel, pump2StatusLabel, lastRunTimeLabel, window, client_Addr, settings, sendSocket)
runButton = Button(master=buttons, text="Run Pumps", fg="red", command=lambda: cmds.runBothPumps())
scheduleButton = Button(master=buttons, text='Edit Schedule', fg='red', command=lambda: settingsMenu())
graph.draw()

graph.get_tk_widget().grid(row=0, column=4)

# toolbar = NavigationToolbar2Tk(graph, window)

window.columnconfigure(0, weight=1)
window.rowconfigure(1, weight=1)

labels.columnconfigure(0, weight=1)
labels.rowconfigure(1, weight=1)

# graphFrame.columnconfigure(1, weight=2)
# graphFrame.rowconfigure(0, weight=2)

dateTimeLabel.pack()
lastRunLabel.pack()
lastRunTimeLabel.pack()
connLabel.pack()
connStatusLabel.pack()
pump1Label.pack()
pump1StatusLabel.pack()
pump2Label.pack()
pump2StatusLabel.pack()
runButton.pack()
scheduleButton.pack()

updateTime()
pump = PumpThread.pumpThread(sendSocket, settings, cmds)
pump.start()
serv = Server.Server(dataQueue, recvSocket)
serv.start()
window.after(100, processQueue)
window.after(50, shutdownCheck())
window.attributes('-fullscreen', True)
window.mainloop()

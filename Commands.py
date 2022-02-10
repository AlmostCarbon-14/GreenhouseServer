from datetime import datetime
import time

class Commands:
    def __init__(self, p1Label, p2Label, window, clientAddr, settings, sendSocket):
        self.p1Label = p1Label
        self.p2Label = p2Label
        self.window = window
        self.clientAddr = clientAddr
        self.settings = settings
        self.sendSocket = sendSocket

    def sendPacket(self, code, runTime):
        self.sendSocket.sendto(f"{code},{runTime}".encode(), self.clientAddr)

    def runPump1(self):
        self.p1Label.config(text='On', foreground='green')
        self.window.update()
        self.sendPacket(555, self.settings['pump1Runtime'])

    def runPump2(self):
        self.p2Label.config(text='On', foreground='green')
        self.window.update()
        self.sendPacket(560, self.settings['pump2Runtime'])

    def runBothPumps(self):
        self.runPump1()
        time.sleep(self.settings['pump1Runtime'] + 5)
        self.p1Label.config(text='Off', foreground='red')
        self.window.update()

        self.runPump2()
        time.sleep(self.settings['pump2Runtime'] + 5)
        self.p2Label.config(text='Off', foreground='red')

        self.p2Label.config(text=f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}", foreground='green')

    def updateSettings(self, newSettings):
        self.settings = newSettings
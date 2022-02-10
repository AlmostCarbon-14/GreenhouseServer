import threading
import time
import Commands
from datetime import datetime, date, timedelta


class pumpThread(threading.Thread):
    def __init__(self, sendSocket, settings, cmds):
        super().__init__()
        self.sendSocket = sendSocket
        self.settings = settings
        self.cmds = cmds
        self._kill = False
        self._ranToday = False

    def _getDOTW(self):
        return self.settings['DOTW'][datetime.today().weekday()]

    def killThread(self):
        self._kill = True

    def run(self):
        while not self._kill:
            if self._getDOTW() != 1 or self._ranToday:
                midnight = ((23 - datetime.now().hour) * 60) + (60 - datetime.now().minute) + 2
                tomorrow = datetime.now() + timedelta(minutes=midnight)
                if (tomorrow - datetime.now()).total_seconds() > 60:
                    time.sleep(60)
                else:
                    self._ranToday = False
            else:
                pumpTime = (abs((int(self.settings['runTimeH']) - datetime.now().hour)) * 60) + (int(self.settings['runTimeM']) - datetime.now().minute)
                runPumpAt = datetime.now() + timedelta(minutes=pumpTime)
                if (runPumpAt - datetime.now()).total_seconds() > 10:
                    time.sleep(10)
                else:
                    self.cmds.runBothPumps()
                    self._ranToday = True





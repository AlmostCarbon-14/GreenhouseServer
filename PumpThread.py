import threading


class pumpThread(threading.Thread):
    def __init__(self, sendSocket, settings, cmds):
        super().__init__()
        self.sendSocket = sendSocket
        self.settings = settings
        self._kill = False
        self.cmds = cmds


    def killThread(self):
        self._kill = True

    def run(self):
        while not self._kill:
            pass

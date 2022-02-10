import threading
import Commands

class Server(threading.Thread):
    def __init__(self, queue, recvSocket, cmds):
        super().__init__()
        self.queue = queue
        self.recvSocket = recvSocket
        self.commands = cmds

    def run(self):
        while True:
            packet = self.recvSocket.recvfrom(1024)
            msg = packet[0]
            self.queue.put(msg.decode())

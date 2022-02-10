import threading


class Server(threading.Thread):
    def __init__(self, queue, recvSocket):
        super().__init__()
        self.queue = queue
        self.recvSocket = recvSocket

    def run(self):
        while True:
            packet = self.recvSocket.recvfrom(1024)
            msg = packet[0]
            self.queue.put(msg.decode())

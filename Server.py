from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import socket
IP_ADDR = '192.168.1.112'
SEND_PORT = 6556
RECV_PORT = 6557

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = (IP_ADDR, SEND_PORT)
sock.bind(address)

while True:
    print(f"{'*'*32}Listening on {socket.gethostbyname(socket.gethostname())}{'*'*32}")
    client_data, client_addr = sock.recvfrom(4096)
    print(f"Data Recieved From {client_addr}\n\n\t{client_data.decode('utf-8')}\n")
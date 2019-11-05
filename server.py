
import socket
import cv2 as cv
import numpy
from multiprocessing import Queue
from _thread import *

enclosure_queue = Queue()


# thread function
def threaded(client_socket, addr, queue):
    print('connected by :', addr[0], ':', addr[1])
    while True:
        try:
            data = client_socket.recv(1024)

            if not data:
                print('disconnected by ' + addr[0], ':', addr[1])
                break

            stringData = queue.get()
            client_socket.send(str(len(stringData)).ljust(16).encode())
            client_socket.send(stringData)

        except ConnectionResetError as e:
            print('Disconnected by ' + addr[0], ':', addr[1])
            break

    client_socket.close()


# 10.10.23.34 num 5 pos ip
# 10.10.23.10 num 10 pos ip
IP = '10.10.23.10'
PORT = 8000

# AF_INET : IPv4, AF_INET6 : IPv6, SOCK_DGRAM : UDP, SOCK_STREAM : TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen(0)

print('server start')
print('server ip: {:s} | port: {:d}'.format(IP, PORT))

while True:
    print('wait')
    client_socket, addr = server_socket.accept()

    k = cv.waitKey(1)
    if k == 27:
        break

server_socket.close()

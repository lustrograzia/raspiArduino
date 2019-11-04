
import socket
import cv2 as cv
import numpy
from queue import Queue
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


def webcam(queue):

    capture = cv.VideoCapture(-1)

    while True:
        ret, frame = capture.read()

        if ret == False:
            continue

        encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv.imencode('.jpg', frame, encode_param)

        data = numpy.array(imgencode)
        stringData = data.tostring()

        queue.put(stringData)

        cv.imshow('image', frame)

        key = cv.waitKey(1)
        if key == 27:
            break


IP = '10.10.23.10'
PORT = 8000

# AF_INET : IPv4, SOCK_DGRAM : UDP, SOCK_STREAM : TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()

print('server start')
print('server ip: {:s} | port: {:d}'.format(IP, PORT))

start_new_thread(webcam, (enclosure_queue,))

while True:
    print('wait')

    client_socket, addr = server_socket.accept()
    start_new_thread(threaded, (client_socket, addr, enclosure_queue,))

server_socket.close()

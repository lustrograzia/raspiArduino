
import socket
import numpy as np
import cv2 as cv


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


IP = '10.10.23.10'
PORT = 8000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

while True:

    message = '1'
    client_socket.send(message.encode())

    length = recvall(client_socket, 16)
    stringData = recvall(client_socket, int(length))
    data = np.frombuffer(stringData, dtype=np.uint8)

    decimg = cv.imdecode(data, 1)
    cv.imshow('image', decimg)

    key = cv.waitKey(1)
    if key == 27:
        break

client_socket.close()

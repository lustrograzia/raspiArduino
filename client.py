
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


def web_cam(queue):

    capture = cv.VideoCapture(-1)
    ret, frame = capture.read()

    encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 90]
    result, img_encode = cv.imencode('.jpg', frame, encode_param)

    img_data = np.array(img_encode)
    string_data = img_data.tostring()

    queue.put(string_data)

    cv.imshow('image', frame)


IP = '10.10.23.10'
PORT = 8000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

message = '1'
client_socket.send(message.encode())

"""
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
"""

client_socket.close()

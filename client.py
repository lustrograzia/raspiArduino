
import socket
import numpy as np
import cv2 as cv
import serial


def web_cam(queue):

    capture = cv.VideoCapture(-1)
    ret, frame = capture.read()

    encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 90]
    result, img_encode = cv.imencode('.jpg', frame, encode_param)

    img_data = np.array(img_encode)
    string_data = img_data.tostring()

    queue.put(string_data)

    cv.imshow('image', frame)


def send_img(socket_name):
    capture = cv.VideoCapture(-1)
    ret, frame = capture.read()

    pre_message = 'cv_img'
    socket_name.send(pre_message.encode())

    encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 90]
    result, img_encode = cv.imencode('.jpg', frame, encode_param)
    img_data = np.array(img_encode)
    string_data = img_data.tostring()

    socket_name.send(str(len(string_data)).ljust(16))
    socket_name.send(string_data)


IP = '10.10.23.10'
PORT = 8000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

sequence = 0

while True:
    if sequence is 0:
        sequence = input('insert number\n'
                         '1 send ready message\n'
                         '2 prepared receive data\n'
                         '3 transfer img\n'
                         '9 stop\n')
    elif sequence is 1:
        print('sequence 1')
        message = 'ready'
        client_socket.send(message.encode())
        sequence = 3
    elif sequence is 2:
        print('sequence 2')
        server_data = client_socket.recv(1024)
        server_message = server_data.decode()
        if server_message == 'transfer img':
            sequence = 3
    elif sequence is 3:
        print('sequence 3')
        send_img(client_socket)
        sequence = 2
    elif sequence is 9:
        print('sequence 9')
        break
client_socket.close()

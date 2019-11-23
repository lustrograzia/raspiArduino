
import socket
import numpy as np
import cv2 as cv
import serial
import time
import m_vision as mv
import sys


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
    sys.stdout.flush()
    capture = cv.VideoCapture(-1)
    ret, frame = capture.read()
    frame = cv.flip(frame, 0)
    frame = cv.flip(frame, 1)
    capture.release()

    encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 90]
    result, img_encode = cv.imencode('.jpg', frame, encode_param)
    img_data = np.array(img_encode)
    string_data = img_data.tostring()

    pre_message = 'cv_img'
    socket_name.send(pre_message.encode())
    socket_name.send(str(len(string_data)).ljust(16))
    socket_name.send(string_data)

    cv.imshow('img', frame)


IP = '10.10.23.10'
PORT = 8000
serial_port = '/dev/ttyACM0'
sequence = 0
first_send_img = True

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

while True:
    if sequence is 0:
        mv.now_time()
        sequence = input('insert number\n'
                         '1 receive server data\n'
                         '3 transfer img\n'
                         '5 ready transfer\n'
                         '9 stop\n')
    elif sequence is 1:
        print('sequence 1 : receive server data')
        mv.now_time()
        client_data = client_socket.recv(1024)
        client_message = client_data.decode()
        print(client_message)
        if client_message == 'move left':
            sequence = 5
        elif client_message == 'move right':
            sequence = 6
        elif client_message == 'check object position':
            sequence = 0
    elif sequence is 3:
        print('sequence 3 : transfer img')
        mv.now_time()
        send_img(client_socket)
        sequence = 1
    elif sequence is 5:
        mv.now_time()
        print('sequence 5 : robotic arm rotate left')
        ard = serial.Serial(serial_port, 9600)
        ard.write('L'.encode())
        time.sleep(1)
        sequence = 3
    elif sequence is 6:
        mv.now_time()
        print('sequence 6 : robotic arm rotate right')
        ard = serial.Serial(serial_port, 9600)
        ard.write('R'.encode())
        time.sleep(1)
        sequence = 3
    elif sequence is 9:
        print('sequence 9')
        break
client_socket.close()

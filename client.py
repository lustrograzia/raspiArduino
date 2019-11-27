
import socket
import numpy as np
import cv2 as cv
import serial
import time
import m_vision as mv


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
    frame = cv.flip(frame, 0)
    frame = cv.flip(frame, 1)
    capture.release()

    encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 90]
    result, img_encode = cv.imencode('.jpg', frame, encode_param)
    img_data = np.array(img_encode)
    string_data = img_data.tostring()

    socket_name.send(str(len(string_data)).ljust(16))
    socket_name.send(string_data)


IP = '192.168.0.17'
PORT = 8000
serial_port = '/dev/ttyACM0'
sequence = 0
first_send_img = True
n = 0

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
ard = serial.Serial(serial_port, 9600)

while True:
    if sequence is 0:
        mv.now_time()
        sequence = input('insert number\n'
                         '1 receive server data\n'
                         '2 transfer one image\n'
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
            client_data = client_socket.recv(1024)
            client_message = client_data.decode()
            n = int(client_message)
            sequence = 5
        elif client_message == 'move right':
            client_data = client_socket.recv(1024)
            client_message = client_data.decode()
            n = int(client_message)
            sequence = 6
        elif client_message == 'client init':
            sequence = 0
        elif client_message == 'pick sequence 0':
            sequence = 7
        elif client_message == 'send img':
            sequence = 3
    elif sequence is 2:
        print('sequence 2 : transfer one image')
        client_socket.send('transfer one image'.encode())
        send_img(client_socket)
        sequence = 0
    elif sequence is 22:
        print('sequence 22 : input data send arduino')
        message = raw_input('command:')
        if message == 'exit':
            sequence = 0
            continue
        elif message == '2':
            sequence = 2
            continue
        ard.write(message)
    elif sequence is 3:
        print('sequence 3 : transfer img')
        mv.now_time()
        client_socket.send('cv_img'.encode())
        send_img(client_socket)
        sequence = 1
    elif sequence is 4:
        print('sequence 4 : delay start')
        time.sleep(10)
        sequence = 3
    elif sequence is 5:
        print('sequence 5 : robotic arm rotate left', mv.now_time())
        for _ in range(n):
            ard.write('L;'.encode())
        time.sleep(1)
        sequence = 3
    elif sequence is 6:
        print('sequence 6 : robotic arm rotate right', mv.now_time())
        for _ in range(n):
            ard.write('R;'.encode())
        time.sleep(1)
        sequence = 3
    elif sequence is 7:
        # pick sequence 0
        print('sequence 7 : pick sequence 0')
        ard.write('v100;h50;')
        time.sleep(2)
        ard.write('v0;')
        time.sleep(1)
        # pick sequence 1
        client_socket.send('pick sequence 1'.encode())
        while True:
            send_img(client_socket)
            client_message = client_socket.recv(1024).decode()
            if client_message == 'pick sequence 2':
                break
            ard.write(client_message)
        # pick sequence 2
        print('sequence 7 : pick sequence 2')
        ard.write('p75;')
        time.sleep(3)
        ard.write('h50;')
        time.sleep(2)
        ard.write('v50;r150;')
        time.sleep(2)
        ard.write('v0;')
        time.sleep(2)
        ard.write('p0;')
        time.sleep(1)
        ard.write('i;')
        sequence = 0
    elif sequence is 9:
        print('sequence 9')
        client_socket.send('end'.encode())
        break
client_socket.close()

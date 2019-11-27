
# raspberry pi only send img

import socket
import numpy as np
import cv2 as cv
import m_vision as mv


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


IP = '10.10.23.10'
PORT = 8000
sequence = 1

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

while True:
    mv.now_time()
    if sequence is 0:
        sequence = input('insert number\n'
                         '1 receive server data\n'
                         '2 transfer one image\n'
                         '3 transfer img\n'
                         '9 stop\n')
    elif sequence is 1:
        print('sequence 1 : receive server data')
        server_message = client_socket.recv(1024).decode()
        print(server_message)
        if server_message == 'client init':
            sequence = 0
        elif server_message == 'send img':
            sequence = 3
        elif server_message == 'exit':
            sequence = 9
    elif sequence is 3:
        print('sequence 3 : transfer img')
        send_img(client_socket)
        sequence = 1
    elif sequence is 9:
        print('sequence 9')
        break
client_socket.close()

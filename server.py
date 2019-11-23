
import socket
import cv2 as cv
import numpy as np
from multiprocessing import Queue
from _thread import *
import m_vision as mv
from datetime import datetime
import sys
import math

enclosure_queue = Queue()
first_img = None
move_left = None


def receive_img_data(socket_name, count):
    temp_buf = b''
    while count:
        new_buf = socket_name.recv(count)
        if not new_buf:
            print('not new_buf')
            return None
        temp_buf += new_buf
        count -= len(new_buf)
    return temp_buf


def decode_img(socket_name):
    length = receive_img_data(socket_name, 16)
    string_data = receive_img_data(socket_name, int(length))
    img_data = np.fromstring(string_data, dtype=np.uint8)
    decode_img_data = cv.imdecode(img_data, 1)
    now = datetime.now()
    name = now.strftime('%Y%m%d_%H%M%S')
    cv.imwrite('d:/doc/pic/test/' + name + '.jpg', decode_img_data)
    return decode_img_data


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

sequence = 0
client_socket = None
first_point = None
second_point = None
received_img = None

while True:
    # sequence 0: wait connect client
    # sequence 1: receive image data
    # sequence 2: extract center point
    # sequence 3: move robotic arm
    # sequence 8: not detected circles in received image
    if sequence is 0:
        # wait connect
        print('waiting...')
        client_socket, address = server_socket.accept()
        print('Connected by', address[0], ':', address[1])
        sequence = 1
    elif sequence is 1:
        # receive client data
        print('sequence : 1')
        mv.now_time()
        client_data = client_socket.recv(1024)
        client_message = client_data.decode()
        print(client_message)
        if client_message == 'cv_img':
            received_img = decode_img(client_socket)
            sequence = 11
    elif sequence is 11:
        center = mv.color_object_extract(received_img)
        if center == -1:
            print('not have point')
            sequence = 1
            continue
        if first_point is None:
            first_point = center
            message = 'move right'
            client_socket.send(message.encode())
            sequence = 1
        else:
            second_point = center
            sequence = 12
    elif sequence is 12:
        print(first_point, second_point)
        message = 'check object position'
        client_socket.send(message.encode())
        sequence = 5
    elif sequence is 2:
        # extract circles
        print('sequence : 2')
        mv.now_time()
        if received_img is not None:
            center = mv.color_object_extract(received_img)
            if center is -1:
                received_img = None
                sequence = 8
            else:
                if first_point is None:
                    first_point = center
                    sequence = 3
                else:
                    second_point = center
                    sequence = 9
        else:
            # receive_img is None
            sequence = 8
    elif sequence is 3:
        # move robotic arm
        print('sequence : 3')
        mv.now_time()
        message = ''
        if first_point[0] > 330:
            message = 'move left'
            move_left = True
        elif first_point[0] < 310:
            message = 'move right'
            move_left = False
        else:
            print('object placed center')
        client_socket.send(message.encode())
        sequence = 1
    elif sequence is 5:
        # calculate position
        print('sequence : 5')
        PI = 3.14159265358979
        DEGREE = PI / 180
        theta_a = mv.pixel_to_angle(first_point)
        theta_b = mv.pixel_to_angle(second_point)
        theta_c = 20
        len_origin = 104 - 90

        m1 = math.tan(DEGREE * (90 - theta_a))
        m2 = math.tan(DEGREE * (90 - theta_b - theta_c))
        p1x = 0
        p1y = len_origin * -1
        p2x = len_origin * -1 * math.sin(DEGREE * theta_c)
        p2y = len_origin * -1 * math.cos(DEGREE * theta_c)
        k1 = p1y - p1x * m1
        k2 = p2y - p2x * m1
        p3x = (k2 - k1) / (m1 - m2)
        p3y = m1 * p3x + k1
        L = math.sqrt(math.pow(p3x, 2) + math.pow(p3y, 2))
        theta = L * math.acos(p3x / L)
        print('t_a:', theta_a)
        print('t_b:', theta_b)
        print('t_c:', theta_c)
        print('L0:', len_origin)
        print('m1:', m1)
        print('m2:', m2)
        print('p1x:', p1x)
        print('p1y:', p1y)
        print('p2x:', p2x)
        print('p2y:', p2y)
        print('p3x:', p3x)
        print('p3y:', p3y)
        print('k1:', k1)
        print('k2:', k2)
        print('L:', L)
        print('theta:', theta)
        sequence = 1
    elif sequence is 8:
        # not detected circles in received image
        print('sequence : 8')
        message = 'check object position'
        client_socket.send(message.encode())
        sequence = 1
    elif sequence is 9:
        print('sequence : 9')
        break

    if client_socket is None:
        sequence = 0
        continue

cv.destroyAllWindows()
server_socket.close()

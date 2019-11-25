
import socket
import cv2 as cv
import numpy as np
from multiprocessing import Queue
from _thread import *
import m_vision as mv
from datetime import datetime
import sys
import math
import time

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
    return decode_img_data


def show_angle_img(img):
    x = 640 / 62.2 * 10
    cv.line(img, (320, 0), (320, 480), (0, 0, 255))
    x0 = int(x)
    n = 0
    while x0 < 640:
        x0 = int(x * n)
        n += 1
        cv.line(img, (x0, 0), (x0, 480), (0, 0, 255))
    cv.imshow('line img', img)


def write_img(img):
    now = datetime.now()
    name = now.strftime('%Y%m%d_%H%M%S')
    cv.imwrite('d:/doc/pic/test/' + name + '.jpg', img)


def pick_sequence(socket_name):
    print('pick sequence 0')
    socket_name.send('pick sequence 0'.encode())
    client_message = client_socket.recv(1024).decode()
    if client_message == 'pick sequence 1':
        print('pick sequence 1')
        h = 50
        while True:
            received_img = decode_img(client_socket)
            contour_area = mv.color_object_extract(received_img, area=1)
            write_img(received_img)
            print(contour_area)
            if contour_area < 30000:
                h += 30
                message = 'h' + str(h) + ';'
                socket_name.send(message.encode())
            elif contour_area < 40000:
                h += 10
                message = 'h' + str(h) + ';'
                socket_name.send(message.encode())
            elif contour_area < 70000:
                h += 5
                message = 'h' + str(h) + ';'
                socket_name.send(message.encode())
            else:
                print('pick sequence 2')
                socket_name.send('pick sequence 2'.encode())
                break
    else:
        print('pick sequence 1 error')


# 10.10.23.34 num 5 pos ip
# 10.10.23.10 num 10 pos ip
# 10.10.23.11 num 11 pos ip
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
            sequence = 12
        elif client_message == 'transfer one image':
            sequence = 15
        elif client_message == 'end':
            sequence = 9
    elif sequence is 11:
        # receive img and calculate distance
        print('sequence : 11')
        received_img = decode_img(client_socket)

        center = mv.color_object_extract(received_img)
        if center == -1:
            print('not have point')
            client_socket.send('client init'.encode())
            sequence = 1
            continue
        if first_point is None:
            cv.putText(received_img, 'first', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
            write_img(received_img)
            first_point = center
            if center[0] > 320:
                client_socket.send('move right'.encode())
                #client_socket.send('20'.encode())
                sequence = 1
            else:
                client_socket.send('move left'.encode())
                #client_socket.send('20'.encode())
                sequence = 1
        elif second_point is None:
            second_point = center
            client_socket.send('send img'.encode())
            sequence = 1
        else:
            if second_point == center:
                second_point = center
                cv.putText(received_img, 'second', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
                write_img(received_img)
                print(first_point, second_point)
                client_socket.send('client init'.encode())
                sequence = 5
            else:
                second_point = center
                client_socket.send('send img'.encode())
                sequence = 1
    elif sequence is 12:
        print('sequence : 12')
        received_img = decode_img(client_socket)
        center = mv.color_object_extract(received_img)
        if center == -1:
            print('not have point')
            sequence = 1
            continue
        print(center)
        # cam_angle = 57.26
        cam_angle = 62.2
        angle = cam_angle / 640 * center[0]
        print('angle :', angle)
        if angle < cam_angle / 2:
            angle = str(int(cam_angle / 2 - angle))
        else:
            angle = str(int(angle - cam_angle / 2))
        print('angle :', angle)
        if center[0] > 325 and int(angle) > 0:
            client_socket.send('move right'.encode())
            client_socket.send(angle.encode())
            sequence = 1
        elif center[0] < 315 and int(angle) > 0:
            client_socket.send('move left'.encode())
            client_socket.send(angle.encode())
            sequence = 1
        else:
            print('align center', center[0])
            # pick sequence
            pick_sequence(client_socket)
            sequence = 1
    elif sequence is 15:
        # receive one image
        received_img = decode_img(client_socket)
        # write image
        now = datetime.now()
        name = now.strftime('%Y%m%d_%H%M%S')
        cv.imwrite('d:/doc/pic/test/' + name + '.jpg', received_img)
        # show contour
        center, result = mv.color_object_extract(received_img, 1)
        if center is not -1:
            print(center)
            cv.imshow('contour', result)
            cv.waitKey()
            cv.destroyAllWindows()
        sequence = 1
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
        theta_a, a_direction = mv.pixel_to_angle(first_point)
        theta_b, b_direction = mv.pixel_to_angle(second_point)
        if a_direction is not b_direction:
            theta_b = theta_b * -1
        theta_c = 20
        # len_origin = 104 - 90
        len_origin = 155

        m1 = math.tan(DEGREE * (90 - theta_a))
        m2 = math.tan(DEGREE * (90 - theta_b - theta_c))
        p1x = 0
        p1y = len_origin
        p2x = len_origin * math.sin(DEGREE * theta_c)
        p2y = len_origin * math.cos(DEGREE * theta_c)
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
        first_point = None
        second_point = None
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

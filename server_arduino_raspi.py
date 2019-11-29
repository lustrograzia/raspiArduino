
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
import serial


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


def read_value_list(find=None):
    ard.write(b'm;')
    while True:
        msg = ard.readline().decode()
        find_value = msg.find('value')
        if find_value != -1:
            break
    msg = msg.strip().split('  ')
    msg = [i.split(' = ') for i in msg]
    if find is None:
        return msg
    else:
        for i in msg:
            if i[0] == find:
                return int(float(i[1]))
        return -1


def confirm_move():
    msg = ard.readline().decode().strip()
    if msg is 'y': return True
    else: return False


# 10.10.23.3 num 3 pos ip
# 10.10.23.4 num 4 pos ip
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

# sequence 3 loop command
extract_object = False
align_center = False
set_bottom = False
pre_center = [0, 0]
align_h = False
align_v = False
move_sequence = 0
move_bottom = False
wait_response = False

serial_port = "COM7"
ard = serial.Serial(serial_port, 115200)

while True:
    # mv.now_time()
    if sequence is 0:
        # wait connect
        print('waiting...')
        client_socket, address = server_socket.accept()
        print('Connected by', address[0], ':', address[1])
        sequence = 1
    elif sequence is 1:
        sequence = int(input('sequence 2 : receive client message\n'
                             'sequence 3 : receive client img\n'
                             'sequence 9 : exit\n'))
    elif sequence is 2:
        # receive client data
        print('sequence : 2')
        client_data = client_socket.recv(1024)
        client_message = client_data.decode()
        print(client_message)
    elif sequence is 3:
        # receive client img
        print('sequence 3 : receive client img')
        client_socket.send('send img'.encode())
        received_img = decode_img(client_socket)

        k = cv.waitKey(1)
        if k == 27:
            cv.destroyWindow('img')
            sequence = 1
            continue
        elif k == ord('s'):
            extract_object = not extract_object
        elif k == ord('k'):
            mv.now_time()
            align_center = not align_center
        elif k == ord('m'):
            print(read_value_list())

        if extract_object:
            area, center, object_img = mv.color_object_extract(received_img)
            if area is not -1 or set_bottom is True:
                print(pre_center, center, end=" ")
                received_img = object_img
                if move_sequence is 3 and area > 100000:
                    move_sequence = 4
                if wait_response:
                    m = ard.readline().decode()
                    print(m)
                    m = m.strip()
                    if m is 'y':
                        wait_response = False
                else:
                    if align_center:
                        if abs(center[0] - 320) > 10:
                            r = read_value_list('value[0]')
                            print('r:', r, end=" ")
                            r -= int(62.2 / 640 * (center[0] - 320))
                            ard.write(('r' + str(r)).encode())
                            time.sleep(0.2)
                        else:
                            print('align h center')
                            align_h = True
                            align_center = False
                            move_sequence = 1
                        wait_response = True
                    if move_sequence:
                        print(area)
                        if move_sequence is 1:
                            ard.write('a1h100v-20'.encode())
                            time.sleep(1)
                            move_sequence = 15
                        elif move_sequence is 15:
                            ard.write('a0'.encode())
                            move_sequence = 2
                        elif move_sequence is 2:
                            if abs(center[0] - 320) > 20:
                                r = read_value_list('value[0]')
                                print('r:', r, end=" ")
                                r -= int(62.2 / 640 * (center[0] - 320) / 2)
                                ard.write(('r' + str(r)).encode())
                            elif abs(center[1] - 240) > 40:
                                    n = read_value_list('value[3]')
                                    print('n:', n, end=" ")
                                    n -= int(62.2 / 640 * (center[0] - 320) / 2)
                                    ard.write(('n' + str(n)).encode())
                            else:
                                move_sequence = 3
                        elif move_sequence is 3:
                            if abs(pre_center[1] - center[1]) < 30:
                                if area < 50000:
                                    h = read_value_list('h')
                                    h += 40
                                    ard.write(('h' + str(h)).encode())
                                elif area < 70000:
                                    h = read_value_list('h')
                                    h += 30
                                    ard.write(('h' + str(h)).encode())
                                elif area < 100000:
                                    h = read_value_list('h')
                                    h += 20
                                    ard.write(('h' + str(h)).encode())
                        elif move_sequence is 4:
                            """
                            ard.write('p70'.encode())
                            time.sleep(3)
                            ard.write('a1v50h100'.encode())
                            time.sleep(2.5)
                            ard.write('r170'.encode())
                            time.sleep(3)
                            ard.write('v-30'.encode())
                            time.sleep(2)
                            ard.write('p0'.encode())
                            time.sleep(2)
                            ard.write('v50'.encode())
                            time.sleep(2)
                            ard.write('r90v100h0'.encode())
                            """
                            ard.write('s'.encode())
                            move_bottom = False
                            extract_object = False
                            move_sequence = 0
                        wait_response = True
                pre_center = [int((pre_center[0] + center[0]) / 2), int((pre_center[1] + center[1]) / 2)]

        cv.imshow('img', received_img)
    elif sequence is 4:
        # serial communicate
        print('sequence 4 : serial communicate')
        command = input('command:')

        if command == 'exit':
            sequence = 1
            continue
        ard.write(command)
    elif sequence is 5:
        # serial read print
        ard.write('q'.encode())
        msg = ard.readline().decode().strip()
        print(msg)
    elif sequence is 9:
        print('sequence : 9')
        client_socket.send('exit'.encode())
        break

cv.destroyAllWindows()
server_socket.close()

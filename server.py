
import socket
import cv2 as cv
import numpy as np
from multiprocessing import Queue
from _thread import *
import m_vision as mv
from datetime import datetime

enclosure_queue = Queue()
first_img = None


# thread function
def threaded(client_socket, addr, queue):
    print('Connected by :', addr[0], ':', addr[1])
    while True:
        try:
            data = client_socket.recv(1024)

            if not data:
                print('disconnected by ' + addr[0], ':', addr[1])
                break

            string_data = queue.get()
            client_socket.send(str(len(string_data)).ljust(16).encode())
            client_socket.send(string_data)

        except ConnectionResetError as e:
            print('Disconnected by ' + addr[0], ':', addr[1])
            print('error:', e)
            break

    client_socket.close()


def receive_img(socket_name, count):
    temp_buf = b''
    while count:
        new_buf = socket_name.recv(count)
        if not new_buf: return None
        temp_buf += new_buf
        count -= len(new_buf)
    return temp_buf


def decode_img(socket_name):
    length = receive_img(socket_name, 16)
    string_data = receive_img(socket_name, int(length))
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
        client_data = client_socket.recv(1024)
        client_message = client_data.decode()
        print(client_message)
        if client_message == 'cv_img':
            receive_img = decode_img(client_socket)
            sequence = 2
    elif sequence is 2:
        # extract circles
        print('sequence : 2')
        if receive_img is not None:
            center = mv.color_object_extract(receive_img)
            if center is -1:
                receive_img = None
                sequence = 8
            else:
                if first_point is None:
                    first_point = center
                else:
                    second_point = center
                # move robotic arm
        else:
            # receive_img is None
            sequence = 8
    elif sequence is 3:
        # move robotic arm
        message = 'ready_second_data'
        client_socket.send(message.encode())
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

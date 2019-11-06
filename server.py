
import socket
import cv2 as cv
import numpy as np
from multiprocessing import Queue
from _thread import *
import m_vision as mv

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

            stringData = queue.get()
            client_socket.send(str(len(stringData)).ljust(16).encode())
            client_socket.send(stringData)

        except ConnectionResetError as e:
            print('Disconnected by ' + addr[0], ':', addr[1])
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
circle_pos = None

while True:

    if sequence is 0:
        # wait connect
        print('waiting...')
        client_socket, address = server_socket.accept()
        print('Connected by', address[0], ':', address[1])
        sequence = 1
    elif sequence is 1:
        print('sequence : 1')
        # receive client data
        if client_socket is None:
            sequence = 0
            continue
        client_data = client_socket.recv(1024)
        client_message = client_data.decode()
        print(client_message)
        if client_message == 'cv_img':
            first_img = decode_img(client_socket)
            sequence = 2
    elif sequence is 2:
        print('sequence : 2')
        if first_img is not None:
            circle_pos = mv.extract_circle(first_img)
            if circle_pos is -1:
                first_img = None
                sequence = 4
            else:
                sequence = 9
        else:
            # first_img is None
            sequence = 4
    elif sequence is 3:
        message = 'resend'
        client_socket.send(message.encode())
        sequence = 1
    elif sequence is 4:
        message = 'check object position'
        client_socket.send(message.encode())
        sequence = 1
    elif sequence is 9:
        break

cv.destroyAllWindows()
server_socket.close()

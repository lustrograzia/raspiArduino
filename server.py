
import socket

ip = '10.10.23.10'
port = 8000

# Start a socket listening for connections on 0.0.0.0:8000
# (0.0.0.0 means all interfaces)

# AF_INET : IPv4, SOCK_DGRAM : UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((ip, port))

print('server start')
print('server ip: {:s} | port: {:d}'.format(ip, port))

while True:
    data, info = server_socket.recvfrom(55555)
    print('client: {:s}/{:d}'.format(info[0], info[1]))
    print('data: {:s}'.format(data.decode()))

    server_socket.sendto(data, info)

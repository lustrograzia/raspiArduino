
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ip = '10.10.23.10'
port = 8000

client_socket.sendto(b'hello', (ip, port))
data = client_socket.recvfrom(55555)
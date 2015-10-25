import sys
import os
import socket
import thread
import time

HOST = 'localhost'
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect((HOST, PORT))
except socket.error as msg:
    print msg
    sys.exit()

server_name = s.getpeername()
print "Connected to server at {0}:{1}".format(server_name[0], server_name[1])

while True:
    s.send("Hello")
    data = s.recv(1024)
    print "Server sent: " + data
    time.sleep(1)

import sys
import os
import socket
import thread
import time

def create_client(host, port, msg = None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # clients.append(s)

    try:
        s.connect((host, port))
    except socket.error as error_msg:
        print error_msg
        sys.exit()

    server_name = s.getpeername()
    client_name = s.getsockname()
    print "Connected to server at {0}:{1} \n".format(server_name[0], server_name[1])

    if msg == None:
        i = 0

    while True:
        if msg == None:
            s.send(str(i))
            i += 1
        else:
            s.send(msg)
        data = s.recv(1024)
        print "Client {0}:{1} received {2} \n".format(client_name[0], client_name[1], data)
        time.sleep(1)

def create_client_thread(host, port, msg = None):
    thread.start_new_thread(create_client, (host, port, msg))

import sys
import os
import signal
import socket
import thread
from multiprocessing import Queue
import time

servers = []
clients = []


def create_client(host, port, msg = None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clients.append(s)

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

def create_server(host, port, queue):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servers.append(s)

    try:
        s.bind((host, port))
    except socket.error as msg:
        print msg
        sys.exit()

    print "Server listening on {0}:{1} \n".format(host, port)

    s.listen(10)

    def clientthread(conn):
        client_name = conn.getpeername()
        while True:
            data = conn.recv(1024)
            print "Server received {0} from {1}:{2}".format(data, client_name[0], client_name[1])
            print "Adding to queue \n"
            queue.put(data)
            reply = "OK " + data
            if not data:
                break
            conn.sendall(reply)
        conn.close()


    while True:
        conn, addr = s.accept()
        print "Connected with {0}:{1} \n".format(addr[0], addr[1])
        thread.start_new_thread(clientthread, (conn,))


    s.close()

def create_listener(queue):
    while True:
        print "Listener received {0} \n".format(queue.get())

def create_client_thread(host, port, msg = None):
    thread.start_new_thread(create_client, (host, port, msg))
def create_server_thread(host, port, queue):
    thread.start_new_thread(create_server, (host, port, queue))
def create_listener_thread(queue):
    thread.start_new_thread(create_listener, (queue,))

def main():
    HOST = 'localhost'
    PORT = 8888

    def signal_handler(signal, frame):
        for server in servers:
            server.close()
        for client in clients:
            client.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    queue = Queue()

    create_server_thread(HOST, PORT, queue)
    create_listener_thread(queue)
    time.sleep(1)
    create_client_thread(HOST, PORT)
    while True:
        pass

if __name__ == "__main__":
    main()

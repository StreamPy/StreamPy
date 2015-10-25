import sys
import os
import signal
import socket
import thread
import time

servers = []
clients = []


def create_client(host, port, msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clients.append(s)

    try:
        s.connect((host, port))
    except socket.error as msg:
        print msg
        sys.exit()

    server_name = s.getpeername()
    print "Connected to server at {0}:{1}".format(server_name[0], server_name[1])

    while True:
        s.send(msg)
        data = s.recv(1024)
        print "Server sent: " + data
        time.sleep(1)

def create_server(host, port):
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
            reply = "OK " + data
            if not data:
                break
            conn.sendall(reply)
        conn.close()


    while True:
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
        thread.start_new_thread(clientthread, (conn,))


    s.close()

def create_client_thread(host, port, msg):
    thread.start_new_thread(create_client, (host, port, msg))
def create_server_thread(host, port):
    thread.start_new_thread(create_server, (host, port))

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

    create_server_thread(HOST, PORT)
    time.sleep(1)
    create_client_thread(HOST, PORT, "Hello from 1")
    time.sleep(1)
    create_client_thread(HOST, PORT, "Hello from 2")
    while True:
        pass

if __name__ == "__main__":
    main()

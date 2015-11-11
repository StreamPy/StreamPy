import sys
import os
import socket
import thread

def create_server(host, port, queue):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # servers.append(s)

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


def create_server_thread(host, port, queue):
    thread.start_new_thread(create_server, (host, port, queue))

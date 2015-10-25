import sys
import os
import socket
import thread

HOST = 'localhost'
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print msg
    sys.exit()

print "Server listening on {0}:{1} \n".format(HOST, PORT)

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

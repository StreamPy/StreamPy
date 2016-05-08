import sys
import os
import socket
import thread
import logging

def create_server(host, port, queue, finished_execution):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind((host, port))
    except socket.error as msg:
        print msg
        sys.exit()

    logging.info("Server listening on {0}:{1}".format(host, port))

    s.listen(10)

    def clientthread(conn):
        client_name = conn.getpeername()
        while True:
            data = conn.recv(1024)
            if not data:
                break
            messages = data.split(";")

            for message in messages:
                if len(message) > 0:
                    logging.info("Server {0}:{1} received {2} from {3}:{4}".format(host, port, message, client_name[0], client_name[1]))
                    queue.put(message)
        conn.close()


    while not finished_execution:
        conn, addr = s.accept()
        logging.info("Server {0}:{1} connected with {2}:{3} \n".format(host, port, addr[0], addr[1]))
        thread.start_new_thread(clientthread, (conn,))
    s.shutdown()
    s.close()


def create_server_thread(host, port, queue, finished_execution):
    thread.start_new_thread(create_server, (host, port, queue, finished_execution))

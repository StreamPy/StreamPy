import requests
import time
from multiprocessing import Queue
import socket

from NodeServer import run_server

class Node():

    def __init__(self, port, debug=False):
        self.processPorts = {}
        self.processes = {}
        self.processInputQueues = {}
        self.processCommandQueues = {}
        self.port = port
        self.next_available_port = 9000
        if debug:
            self.host = 'localhost'
        else:
            self.host = socket.gethostbyname(socket.getfqdn())

        self.initServer()

    def add_process(self, process):
        self.processes[process.id] = process
        self.processInputQueues[process.id] = Queue()
        self.processCommandQueues[process.id] = Queue()
        self.processPorts[process.id] = self.next_available_port + process.id

        self.processes[process.id].start(self.host, self.processPorts[process.id], self.processInputQueues[process.id], self.processCommandQueues[process.id], self)

    def set_master(self, host, port):
        self.masterConn = (host, port)

    def start(self):
        for process_id in self.processCommandQueues:
            self.processCommandQueues[process_id].put('start')

    def get_process_port(self, id):
        return self.processPorts[int(id)]

    def get_process_conn(self, id):

        url = "http://{0}:{1}/processes/{2}".format(self.masterConn[0], self.masterConn[1], id)
        data = requests.get(url=url).content
        conn = data.split(",")
        host = conn[0]
        port = int(conn[1])

        url = "http://{0}:{1}/processes/{2}".format(host, port, id)
        port = requests.get(url=url).content

        return (host, int(port))

    def create_process_conn(self, id):
        print "Creating process connection to process {0}".format(id)
        if id in self.processes:
            print "Process {0} in node".format(id)
            return QueueWrapper(self.processInputQueues[id])
        else:
            print "Creating socket"
            host, port = self.get_process_conn(id)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect((host, port))
            print "Success!"
            return s

    def initServer(self):
        run_server(self)

class QueueWrapper:
    def __init__(self, queue):
        self.queue = queue
    def send(self, message):
        self.queue.put(message)
    def close(self):
        pass

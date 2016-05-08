import dill
import requests
import socket
import time

from MasterServer import run_server

class Master():


    def __init__(self, processes, conns, port, host=None, debug=False):
        self.processes = processes
        self.conns = conns
        self.processesReady = []
        if host is None:
            if debug:
                self.host = 'localhost'
            else:
                self.host = socket.gethostbyname(socket.getfqdn())
        else:
            self.host = host

        self.port = port
        self.processConns = {}
        i = 0
        for process in self.processes:
            self.processConns[process.id] = self.conns[i]
            i += 1
        self.initServer()

        print "Initializing connections"
        self.initializeConnections()

        print "Initializing processes"
        self.initializeProcesses()

        while len(self.processes) != len(self.processesReady):
            pass

        print "Starting processes"
        self.startProcesses()
        while True:
            time.sleep(0.1)

    def initializeConnections(self):
        conf = self.host + ", " + str(self.port)
        for conn in self.conns:
            url = "http://{0}:{1}/conf".format(conn[0], conn[1])
            try:
                requests.post(url, data=conf)
            except requests.exceptions.ConnectionError:
                raise requests.exceptions.ConnectionError("Node server at {0}:{1} refused to connect".format(conn[0], conn[1]))

    def initializeProcesses(self):
        for process in self.processes:
            url = "http://{0}:{1}/processes".format(self.processConns[process.id][0], self.processConns[process.id][1])
            requests.post(url, data=dill.dumps(process))

    def processReady(self, id):
        self.processesReady.append(id)

    def startProcesses(self):
        for conn in self.conns:
            url = "http://{0}:{1}/start".format(conn[0], conn[1])
            requests.post(url)

    def initServer(self):
        run_server(self)

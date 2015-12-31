import dill
import requests
import socket

from MasterServer import run_server

class Master():


    def __init__(self, processes, conns, port, debug=False):
        self.processes = processes
        self.conns = conns

        if debug:
            self.host = 'localhost'
        else:
            self.host = socket.gethostbyname(socket.getfqdn())

        self.port = port
        self.processConns = {}
        i = 0
        for process in self.processes:
            self.processConns[process.id] = self.conns[i]
            i += 1
        self.initServer()
        self.initializeConnections()
        self.initializeProcesses()
        self.startProcesses()

    def initializeConnections(self):
        conf = self.host + ", " + str(self.port)
        for conn in self.conns:
            url = "http://{0}:{1}/conf".format(conn[0], conn[1])
            requests.post(url, data=conf)

    def initializeProcesses(self):
        for process in self.processes:
            url = "http://{0}:{1}/processes".format(self.processConns[process.id][0], self.processConns[process.id][1])
            requests.post(url, data=dill.dumps(process))

    def startProcesses(self):
        for conn in self.conns:
            url = "http://{0}:{1}/start".format(conn[0], conn[1])
            requests.post(url)

    def initServer(self):
        run_server(self)

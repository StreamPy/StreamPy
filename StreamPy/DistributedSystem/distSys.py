import sys
import os
import json
import functions
from AgentProcess import AgentProcess
from Master import Master

def loadFile(filename):
    f = open(filename)
    data = json.load(f)
    f.close()
    return data

def loadConns(conns):
    conns_names = {}
    for name in conns.keys():
        host = conns[name]['host']
        port = int(conns[name]['port'])
        conns_names[name] = (host, port)
    return conns_names


def createProcesses(processes, conns):
    agentProcesses = []
    processConns = []
    ids = {}
    lastUsedId = 0

    # Create ids
    for name in processes.keys():
        ids[name] = lastUsedId
        lastUsedId += 1

    # Create processes
    for key in processes.keys():
        process = processes[key]
        id = ids[key]
        name = process['name']
        input_stream_names = process['input_stream_names']
        output_stream_names = process['output_stream_names']
        conn_name = process['conn']

        if conn_name not in conns:
            print "Error: connection for process {0} not found".format(name)
            sys.exit(1)

        conn = conns[conn_name]
        func = getattr(functions, process['function_name'])
        output_process_list = []
        for process_list in process['output_process_list']:
            process_id_list = []
            for process_name in process_list:
                process_id_list.append(ids[process_name])
            output_process_list.append(process_id_list)
        agentProcess = AgentProcess(id=id, name=key, input_stream_names=input_stream_names,
                                    output_stream_names=output_stream_names,
                                    func=func,
                                    output_process_list=output_process_list)
        agentProcesses.append(agentProcess)
        processConns.append(conn)

    return agentProcesses, processConns

def initializeSystem(processes, conns, host, port, debug=False):
    m = Master(processes, conns, port, host, debug)


def run(filename, host, port):
    data = loadFile(filename)
    conns = loadConns(data['conns'])
    processes, conns = createProcesses(data['processes'], conns)

    try:
        initializeSystem(processes, conns, host, port)
    except Exception, err:
        print err
        sys.exit(0)

if __name__ == "__main__":
    filename = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])

    print "Running {0} on master host {1}, port {2}".format(filename, host, port)

    run(filename, host, port)

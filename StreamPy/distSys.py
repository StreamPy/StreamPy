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


def createProcesses(processes):
    agentProcesses = []
    ids = {}
    lastUsedId = 0

    # Create ids
    for name in processes.keys():
        ids[name] = lastUsedId
        lastUsedId += 1

    # Create processes
    for name in processes.keys():
        process = processes[name]
        id = ids[name]
        input_stream_names = process['input_stream_names']
        output_stream_names = process['output_stream_names']
        func = getattr(functions, process['function_name'])
        output_process_list = []
        for process_list in process['output_process_list']:
            process_id_list = []
            for process_name in process_list:
                process_id_list.append(ids[process_name])
            output_process_list.append(process_id_list)
        agentProcess = AgentProcess(id=id, name=name, input_stream_names=input_stream_names,
                                    output_stream_names=output_stream_names,
                                    func=func,
                                    output_process_list=output_process_list)
        agentProcesses.append(agentProcess)

    return agentProcesses

def initializeSystem(processes, conns, host, port, debug=False):
    m = Master(processes, conns, port, host, debug)

def runFile(filename):
    data = loadFile(filename)
    processes = createProcesses(data['processes'])
    conns = [('localhost', 8000), ('localhost', 8001), ('localhost', 8002)] 
    masterHost = 'localhost'
    masterPort = 9030
    initializeSystem(processes, conns, masterHost, masterPort)


if __name__ == "__main__":
    filename = sys.argv[1]
    runFile(filename)

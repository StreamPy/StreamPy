import sys
import os
import time

from AgentProcess import AgentProcess
from Master import Master


import multiprocessing
from multiprocessing import Process, Queue
import threading
from RemoteQueue import RemoteQueue
import socket
import thread
import json
from server import create_server_thread
import logging



def random_ints(input_streams, output_streams):
    from random import randint
    from Stream import Stream, _close, _no_value
    from Operators import stream_agent, stream_agent
    # Append random numbers to output_streams[0]
    # The numbers are in the interval (0, 99).
    N = 10
    for i in range(N):
        element_of_stream = randint(0,99)
        output_streams[0].append(element_of_stream)
        print 'In random_ints. element = ', element_of_stream
        #time.sleep(0.1)

    # Close this stream
    output_streams[0].append(_close)


# The single output stream returns the function f
# applied to elements of the single input stream.
# When the input stream is closed, also close the
# output stream.
def apply_func_agent(input_streams, output_streams):
    from Stream import Stream, _close, _no_value
    from Operators import stream_agent, stream_agent

    def f(v): return 2*v

    input_stream = input_streams[0]
    output_stream = output_streams[0]

    def apply_func(v):
        # When the input stream is closed, return
        # _close to cause the output stream to close.
        if v == _close:
            return _close
        else:
            print "Apply func"
            return f(v)

    return stream_agent(
        inputs=input_stream,
        outputs=output_stream,
        f_type='element',
        f=apply_func)

# Print the values received on the input stream.
def print_agent(input_streams, output_streams):
    from Stream import Stream, _close, _no_value
    from Operators import stream_agent, stream_agent
    input_stream = input_streams[0]

    def p(v):
        if v != _close:
            print 'print_agent', input_stream.name, v

    return stream_agent(
        inputs=input_stream,
        outputs=[],
        f_type='element',
        f=p)


# This process is a source; it has no input queue
# This process sends simple_stream to queue_1
process_0 = AgentProcess(id=0,
                         input_stream_names=[],
                         output_stream_names=['random_ints_stream'],
                         func=random_ints,
                         output_process_list=[[1]])

# This process receives simple_stream from process_0.
# It sends double_stream to process_2.
# It receives messages on queue_1 and sends messages to queue_2.

process_1 = AgentProcess(id=1,
                         input_stream_names=['random_ints_stream'],
                         output_stream_names=['func_stream'],
                         func=apply_func_agent,
                         output_process_list=[[2]])


# This process is a sink; it has no output queue.
# This process receives double_stream from process_1.
# It prints the messages it receives.
# This process prints [0, 2, ... , 8]

process_2 = AgentProcess(id=2,
                         input_stream_names=['func_stream'],
                         output_stream_names=[],
                         func=print_agent,
                         output_process_list=[])

processes = [process_0, process_1, process_2]
host = "131.215.220.165" # socket.gethostbyname(socket.getfqdn())
conns = [(host, 8990), (host, 8991), (host, 8992)]

open_conns = []
for conn in conns:
    if conn not in open_conns:
        os.system("osascript -e \'tell application \"Terminal\" to do script \"cd $HOME/Documents/Projects/stream-py-networking/;python testNode.py {0} {1}\"\'".format("131.215.220.165", conn[1]))
        open_conns.append(conn)
time.sleep(1)
m = Master(processes, conns, 9999, host="131.215.220.165", debug=False)

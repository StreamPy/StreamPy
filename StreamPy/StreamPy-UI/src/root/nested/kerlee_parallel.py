if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Stream import Stream
from Stream import _no_value, _multivalue
from OperatorsTestParallel import stream_func
from multiprocessing import Process, Queue
from MakeParallelNetworkParallel import *

def main():
    
    # STEP 1
    # PROVIDE CODE OR IMPORT PURE (NON-STREAM) FUNCTIONS
    def generate_numbers(trigger):
        # Expect trigger values to be 1, 2, 3,...
        # return [0, 1, 2] then [3, 4, 5], then [6, 7, 8],..
        result = range(trigger*3, trigger*3+3, 1)
        print 'generating numbers', result
        return _multivalue(result)
        
    def split(v):
        """ Returns [odds, evens]

        """
        #print 'In split. v = ', v
        if v%2:
            return [_no_value, v]
        else:
            return [v, _no_value]

    def mult (v, args):
        #print "In mult, returning ", v*args[0]
        return v*args[0]
    
    def print_message(v, args):
        print '---------In printer process. [', args, '] message = ', v
        return

    # STEP 2 SPECIFY QUEUES, ONE FOR EACH PROCESS.
    # Specify one multiprocessing.Queue for each process
    # in the system, including the "__main__" process.
    
    # Input queue for the source_process
    source_queue = Queue()
    # Input queue for the split_process
    split_queue = Queue()
    # Input queue for the print_process
    print_queue = Queue()

    # STEP 3. SPECIFY THE NETWORK WITHIN EACH PROCESS

    ##############################
    # Specify the source process.
    ##############################

    # Overview:
    # The source process has an input stream, 'trigger_stream'
    # and an output stream, 'source_stream'. When this process
    # gets an integer value on the trigger stream it puts a
    # sequence of messages on source_stream, where the
    # values in the sequence are a function of the value
    # received on the trigger stream.
    
    # STEP 3a. Specify names of all the streams in the network.
    
    # The all_stream_names_tuple includes names of streams coming
    # into the network from outside the network,
    # streams going outside the network from inside the network, 
    # and streams entirely within the network.
    source_all_stream_names_tuple = ('source_stream', 'trigger_stream')
    # The input_stream_names_tuple is a tuple of stream names of
    # streams coming into the network from outside the network.
    source_input_stream_names_tuple = ('trigger_stream',)
    # The output_stream_names_dict is a dict of stream names of
    # streams going from the network to outside the network. The
    # dict key is the stream name and its value is a
    # list consisting of the multiprocessing.Queues to which
    # the messages on this stream go.
    # Note that every key must be in all_stream_names_tuple
    source_output_stream_names_dict = {'source_stream': (split_queue,)}
 
    # STEP 3b. SPECIFY THE AGENTS:
    # Specify an agent_descriptor_dict for this network.
    # The structure of an agent_descriptor_dict is:
    # key: agent name
    # value: (list of input streams, list of output streams, function, function type,
    #        tuple of function arguments, state, call streams)

    source_agent_descriptor_dict = {
        # format is:
        # agent name : [
        #  list of input stream names
        #  list of output stream names
        #  function that implements this agent
        #  function type, e.g. 'element'
        #  function arguments
        #  list of call stream names
        'source_agent': [  # agent name
            ['trigger_stream'],            # list of input stream names. No input stream for this source
            ['source_stream'],    # list of output streams
            generate_numbers, # function for this agent
            'element',     # function type
            None,          # function arguments
            None,          # state
            []    # list of call streams
            ]
        }


    ####################################
    # Specify the split process.
    ####################################
    # Overview:
    # The split process has an input stream, 'source_stream'
    # and two output streams, 'multiples_of_even_stream', and
    # 'multiples_of_odd_stream'. The process receives messages
    # on source stream, sends even numbers to an agent,
    # mult_even_agent, that multiplies the numbers by an
    # argument and puts the result on 'multiples_of_even_stream',
    # and the split process sends odd numbers to an agent,
    # mult_odd_agent, that multiplies the numbers by an
    # argument and puts the result on 'multiples_of_odd_stream'
    
    # STEP 3a. Specify names of all the streams in the network.
    
    # The all_stream_names_tuple includes names of streams coming
    # into the network from outside the network,
    # streams going outside the network from inside the network, 
    # and streams entirely within the network.
    split_all_stream_names_tuple = (
        'source_stream', 'even_stream', 'odd_stream',
        'multiples_of_even_stream', 'multiples_of_odd_stream')
    # The input_stream_names_tuple is a tuple of stream names of
    # streams coming into the network from outside the network.
    split_input_stream_names_tuple = ('source_stream',)
    # The output_stream_names_dict is a dict of stream names of
    # streams going from the network to outside the network. The
    # dict key is the stream name and its value is a
    # list consisting of the multiprocessing.Queues to which
    # the messages on this stream go.
    # Note that every key must be in all_stream_names_tuple
    split_output_stream_names_dict = {
        'multiples_of_even_stream': (print_queue,),
        'multiples_of_odd_stream': (print_queue,)
        }
 
    # STEP 3b. SPECIFY THE AGENTS:
    # Specify an agent_descriptor_dict for this network.
    # The structure of an agent_descriptor_dict is:
    # key: agent name
    # value: (list of input streams, list of output streams, function, function type,
    #        tuple of function arguments, state, call streams)

    split_agent_descriptor_dict = {
        # format is:
        # agent name : [
        #  list of input stream names
        #  list of output stream names
        #  function that implements this agent
        #  function type, e.g. 'element'
        #  function arguments
        #  list of call stream names
        'split_agent': [  # agent name
            ['source_stream'],  # list of input stream names.
            ['even_stream', 'odd_stream'],  # list of output streams.
            split, # function for this agent
            'element',     # function type
            None,          # function arguments
            None,          # state
            []    # list of call streams
            ],
        'mult_even_agent': [    # agent name
            ['even_stream'],    # list of input stream names. 
            ['multiples_of_even_stream'],    # list of output streams.
            mult     , # function for this agent
            'element',     # function type
            (200,),         # function arguments
            None,          # state
            []             # list of call stream names
            ],
        'mult_odd_agent': [    # agent name
            ['odd_stream'],    # list of input stream names. 
            ['multiples_of_odd_stream'],    # list of output streams.
            mult     , # function for this agent
            'element',     # function type
            (1000,),         # function arguments
            None,          # state
            []             # list of call stream names
            ]
        }

    
    ####################################
    # Specify the print process.
    ####################################
    # Overview
    # The print process has two input streams,
    # 'multiples_of_even_stream', and 'multiples_of_odd_stream'.
    # It has two agents that print the values received on the
    # streams.

    # STEP 3a. Specify names of all the streams in the network.
    
    # The all_stream_names_tuple includes names of streams coming
    # into the network from outside the network,
    # streams going outside the network from inside the network, 
    # and streams entirely within the network.
    print_all_stream_names_tuple = (
        'multiples_of_even_stream',
        'multiples_of_odd_stream')
    # The input_stream_names_tuple is a tuple of stream names of
    # streams coming into the network from outside the network.
    print_input_stream_names_tuple = (
        'multiples_of_even_stream',
        'multiples_of_odd_stream',)
    # The output_stream_names_dict is a dict of stream names of
    # streams going from the network to outside the network. The
    # dict key is the stream name and its value is a
    # list consisting of the multiprocessing.Queues to which
    # the messages on this stream go.
    # Note that every key must be in all_stream_names_tuple
    print_output_stream_names_dict = {}
 
    # STEP 3b. SPECIFY THE AGENTS:
    # Specify an agent_descriptor_dict for this network.
    # The structure of an agent_descriptor_dict is:
    # key: agent name
    # value: (list of input streams, list of output streams, function, function type,
    #        tuple of function arguments, state, call streams)

    print_agent_descriptor_dict = {
        # format is:
        # agent name : [
        #  list of input stream names
        #  list of output stream names
        #  function that implements this agent
        #  function type, e.g. 'element'
        #  function arguments
        #  list of call stream names
        'print_even_agent': [  # agent name
            ['multiples_of_even_stream'],  # list of input stream names.
            [],  # list of output streams.
            print_message, # function for this agent
            'element',     # function type
            'even',        # function arguments
            None,          # state
            []    # list of call streams
            ],
        'print_odd_agent': [  # agent name
            ['multiples_of_odd_stream'],  # list of input stream names.
            [],  # list of output streams.
            print_message, # function for this agent
            'element',     # function type
            'odd',          # function arguments
            None,          # state
            []    # list of call streams
            ]
        }

    # MAKE THE PROCESSES

    source_process = Process(
        target=make_process,
        args= (
            source_queue,
            source_all_stream_names_tuple,
            source_input_stream_names_tuple,
            source_output_stream_names_dict,
            source_agent_descriptor_dict)
        )

    split_process = Process(
        target=make_process,
        args= (
            split_queue,
            split_all_stream_names_tuple,
            split_input_stream_names_tuple,
            split_output_stream_names_dict,
            split_agent_descriptor_dict)
        )

    print_process = Process(
        target=make_process,
        args= (
            print_queue,
            print_all_stream_names_tuple,
            print_input_stream_names_tuple,
            print_output_stream_names_dict,
            print_agent_descriptor_dict)
        )

    print '------starting processes----------'
    source_process.start()
    split_process.start()
    print_process.start()

    print'-----adding to queue-----'
    source_queue.put(('trigger_stream', 0))
    source_queue.put(('trigger_stream', 1))
    
if __name__ == '__main__':
    main()


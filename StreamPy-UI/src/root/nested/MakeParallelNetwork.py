from Stream import Stream
from Stream import _no_value, _multivalue
from Agent import Agent

#from OperatorsTest import stream_agent
#from MakeNetworkNew import make_network, network_data_structures
from OperatorsTestParallel import stream_agent
from MakeNetworkParallel import make_network, network_data_structures

from multiprocessing import Process, Queue


def make_input_manager(input_queue, input_stream_dict):
    """ Make an object that waits continuously for a
    message on input_queue and then sends the message
    on the stream with the specified name.

    """
    message = input_queue.get()
    print 'in make input manager, message = ', message
    stream_name, message_content = message
    input_stream_dict[stream_name].append(message)
    input_stream_dict[stream_name].print_recent() 

def make_output_manager(stream_dict, output_stream_names_dict):
    output_stream_names_list = output_stream_names_dict.keys()
    output_stream_list = \
      [stream_dict[stream_name] for stream_name in output_stream_names_list]
    print ' output_stream_names_list',  output_stream_names_list
    print 'output_stream_list', output_stream_list
    
    def send_message_to_queue(value_and_index_tuple):
        message_content, stream_index = value_and_index_tuple
        output_stream_name = output_stream_names_list[stream_index]
        receiver_queue = output_stream_names_dict[output_stream_name]
        message = (output_stream_name, message_content)
        receiver_queue.put(message)

    stream_agent(
        inputs=output_stream_list,
        outputs=None,
        f_type='asynch_element',
        f=send_message_to_queue,
        f_args=None)

def make_process(input_queue,
                 all_stream_names_tuple,
                 input_stream_names_tuple,
                 output_stream_names_dict,
                 agent_descriptor_dict):
    print 'entered make_process'
    print 'input_queue', input_queue
    print 'input_stream_names_tuple', input_stream_names_tuple
    print 'output_stream_names_dict', output_stream_names_dict
    print 'agent_descriptor_dict', agent_descriptor_dict

    stream_dict, agent_dict = \
      make_network(all_stream_names_tuple, agent_descriptor_dict)

    print 'stream_dict', stream_dict
    print 'agent_dict', agent_dict

    input_stream_dict = dict()
    for stream_name in input_stream_names_tuple:
        input_stream_dict[stream_name] = stream_dict[stream_name]
    print 'input_stream_dict', input_stream_dict

    # Create the input stream manager which takes
    # messages from the input queue and appends each message
    # to the specified input stream.
    make_input_manager(input_queue, input_stream_dict)

    # Create the output stream manager which subscribes
    # to messages on streams going outside the process.
    # The output stream manger takes each message m it receives
    # on a stream s and puts m in the input queues of each process
    # that receives s.
    output_manager = make_output_manager(
        stream_dict, output_stream_names_dict)

def main():
    
    # STEP 1
    # PROVIDE CODE OR IMPORT PURE (NON-STREAM) FUNCTIONS
    def generate_numbers():
        print 'in generate numbers'
        return _multivalue(range(5))
    
    def print_message(v):
        print 'In process. message is', v
        return v

    # STEP 2
    # SPECIFY THE NETWORK.

    queue_0 = Queue()
    queue_1 = Queue()
    
    # Specify names of all the streams.
    all_stream_names_tuple = ('source', 'trigger', 'echo')
    input_stream_names_tuple = ('trigger',)
    output_stream_names_dict = {'echo': queue_1}

    # Specify the agents:
    # key: agent name
    # value: list of input streams, list of output streams, function, function type,
    #        tuple of arguments, state
    agent_descriptor_dict = {
        'source_agent': [
            [], ['source'],
            generate_numbers, 'element', None, None, ['trigger']],
        'printer': [
            ['source'], ['echo'],
            print_message, 'element', None, None, None]
        }

    # MAKE THE PROCESS
    ## queue_0 = Queue()
    ## queue_1 = Queue()
    process_0 = Process(target=make_process,
                        args= (queue_0,
                               all_stream_names_tuple,
                               input_stream_names_tuple,
                               output_stream_names_dict,
                               agent_descriptor_dict)
                               )
    process_0.start()
    queue_0.put(('trigger', 0))
    #while not queue_1.empty():
    while True:
        v = queue_1.get()
        print 'v', v

    

if __name__ == '__main__':
    main()


    
    

from Stream import Stream
from Stream import _no_value, _multivalue
from Agent import Agent
from OperatorsTestParallel import stream_agent
from MakeNetworkParallel import make_network, network_data_structures
from multiprocessing import Process, Queue


def make_input_manager(input_queue, input_stream_dict):
    """ Make an object that waits continuously for a
    message on input_queue and then sends the message
    on the stream with the specified name.

    """
    while True:
        message = input_queue.get()
        stream_name, message_content = message
        input_stream_dict[stream_name].append(message_content)
        #input_stream_dict[stream_name].print_recent()


def make_output_manager(stream_dict, output_stream_names_dict):
    output_stream_names_list = output_stream_names_dict.keys()
    output_stream_list = \
      [stream_dict[stream_name] for stream_name in output_stream_names_list]
    
    def send_message_to_queue(value_and_index_tuple):
        """ Append the message on the stream with the specified index
        to each of the queues to which that stream is connected.

        """
        message_content, stream_index = value_and_index_tuple
        output_stream_name = output_stream_names_list[stream_index]
        receiver_queue_list = output_stream_names_dict[output_stream_name]
        #print 'send message to q. message_content = ', message_content
        #print 'send message to q. output_stream_name = ', output_stream_name
        message = (output_stream_name, message_content)
        for receiver_queue in receiver_queue_list:
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

    # Create the network
    # Create all the agents and make the streams connecting them
    stream_dict, agent_dict = \
      make_network(all_stream_names_tuple, agent_descriptor_dict)


    input_stream_dict = dict()
    for stream_name in input_stream_names_tuple:
        input_stream_dict[stream_name] = stream_dict[stream_name]

    # Create the output stream manager which subscribes
    # to messages on streams going outside the process.
    # The output stream manger takes each message m it receives
    # on a stream s and puts m in the input queues of each process
    # that receives s.
    output_manager = make_output_manager(
        stream_dict, output_stream_names_dict)

    # Create the input stream manager which takes
    # messages from the input queue and appends each message
    # to the specified input stream.
    make_input_manager(input_queue, input_stream_dict)

def main():
    
    # STEP 1
    # PROVIDE CODE OR IMPORT PURE (NON-STREAM) FUNCTIONS
    def generate_numbers():
        return_value = _multivalue(range(5))
        print 'in generate_numbers. return value is', return_value
        return return_value
    
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
    output_stream_names_dict = {'echo': (queue_1,)}

    # Specify the agents:
    # key: agent name
    # value: list of input streams, list of output streams, function, function type,
    #        tuple of arguments, state, list of call streams
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


    
    

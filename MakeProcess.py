"""This module makes a mulitprocessing.Process from a function,
func, that maps input streams to output streams. A process
has one input queue of type multiprocessing.Queue. The process
receives messages on its input queue. Each message that it
receives is a tuple (stream name, message content). The process
appends the message content to the stream with the specified
name. This stream must be an input stream of func.

The process sends messages that arrive on output streams of
func to input queues of other processes. Each output stream
is associated with a list of input queues of other processes.
A message on the output stream is copied to each of the queues
associated with that stream. This message is a tuple:
(stream name, message content).

A stream is closed by appending the _close object to the
stream. A process terminates execution when all its input streams
are closed.

Notes
-----
The module consists of three functions:
(1) make_input_manager, which makes an agent that we call
'input manager'
(2) make_output_manager, which makes an agent that we call
'output manager'
(3) make_process, which sets up the data structures for
input and output managers and calls func which creates 
a network of agents that processes input streams and produces
output streams.

The input manager agent gets messages on the process's input
queue and puts them on input streams of func. The output manager
agent gets messages on output streams of func and places copies
of the messages on the input queues of other processes.

"""

from Stream import Stream, _close, _no_value
from Operators import stream_agent, stream_agent
from multiprocessing import Process, Queue
from RemoteQueue import RemoteQueue
import json
import time


def make_input_manager(input_queue, input_stream_names,
                       map_name_to_input_stream):
    """ Makes an object that waits continuously for a
    message arriving on input_queue and then sends the message
    to the stream with the name specified on the message.
    
    Parameters
    ----------
    input_queue: queue
                 Either Multiprocessing.Queue or
                        StreamPy.RemoteQueue
    input_stream_names: list of str
                  The list of names of the input streams.
    
    map_name_to_input_stream : dict
                key : str
                      Name of an input stream.
                value : Stream
                      The stream with that name.

    Attributes
    ----------
    finished_execution : bool
                True if at least one input stream is open
                False if all input streams are closed.

    Returns
    -------
    None

    Notes
    -----
    This agent waits for a message arriving on input_queue.
    Every incoming message is a tuple: (stream_name, message_content)
    The message_content is appended to the stream with the specified
    name. If message_content is _close then the stream is closed
    by the Stream class; the program then sets finished_execution to
    True if all input streams are closed.
    If a message arrives for a closed stream then a warning message
    is attached to the log.
    The input manager continues execution until all its input streams
    are closed, and then stops.
    
    """

    # Initially, by default, all streams are open
    finished_execution = False
    # If the process has no input queue, i.e., if
    # the process is a source, then the process
    # has nothing to do. In this case, set
    # finished_execution to True.
    if not input_queue:
        finished_execution = True

    ## DEBUGGING statements
    ## for key, value in name_to_stream_dict.items():
        ## print 'In make_input_manager'
        ## print 'name_to_stream_dict. key = ', key
        ## print 'name_to_stream_dict. value = ', value
    
    while not finished_execution:
        #print 'entered make_input_manager'
        #print 'input_queue', input_queue
        try:
            message = input_queue.get()
            #print 'in make_input_manager. message = ', message
        except Exception, err:
            print 'Error', err
            return
        # This message_content is to be appended to the
        # stream with name stream_name.
        print 'received message: ', message
        stream_name, message_content = message
        # Get the input_stream to which the message must
        # be appended.
        input_stream = map_name_to_input_stream[stream_name]
        
        if input_stream.closed:
            print 'WARNING: inserting values into a closed stream!'
            return

        if message_content == '_close':
            input_stream.close()
            #for stream in map_name_to_input_stream.values():
                #print 'stream is ', stream
                #print 'stream.closed is', stream.closed
            finished_execution = \
              all([stream.closed for stream in
                   map_name_to_input_stream.values()])
        else:
            #print 'In MakeInputManager, message_content = ', message_content
            #print 'In MakeInputManager, input_stream = ', input_stream
            input_stream.append(message_content)
            #print 'Appended ', message_content
            #print 'In MakeInputManager, input_stream.recent', input_stream.recent[:input_stream.stop]
        # Trying sleep with ActiveMQ to see if that makes a difference.
        #time.sleep(1.0)


def make_output_manager(output_streams, output_queues_list):
    """ Creates an agent, called the output manager, that
    receives messages on streams and inserts these messages
    into queues. The output manager receives messages on all
    streams in the list output_streams and output_streams[j]
    is associated with the list of queues, output_queues_list[j].
    Note that output_queues_list[j] is a list of queues and not a
    singleton queue. A message that arrives on the stream
    output_streams[j] is copied to each of the queues in
    output_queues_list[j]. When a message is placed in a queue
    the message is a tuple (stream_name, message_content).
    Each queue is either Multiprocessing.Queue or
    StreamPy.RemoteQueue.

    Parameters
    ----------
    output_streams : list of Stream
                  list of output streams
    output_queues_list : list of list of Queue
                  list of list of output queues.
                  output_queues_list[j] is the list of queues to which
                  messages in output_streams[j] should be sent.
                  assert len(output_streams) == len(output_queues_list)

    Returns
    -------
    None

    """
    # The sequential program that implements state-transitions of the agent.
    def send_message_to_queue(msg_content_and_stream_index_tuple):
        """ The parameter msg_content_and_stream_index_tuple
        specifies the content of a message and an index, j, which
        specifies a stream, namely output_streams[j].
        Append the message content to the each of the queues
        in the list of queues, output_queues_list[j].
        The message placed on the queue is a tuple
            (output_stream_name, message_content).

        Parameter
        ---------
        msg_content_and_index_tuple: tuple
                   (message_content, stream_index)
                   message_content: value to be inserted into queues of
                                 processes that receive the specified stream.
                   stream_index: int
                                 The slot of the sending stream in the list
                                 output_stream_names_list. 

        """
        message_content, stream_index = msg_content_and_stream_index_tuple
        # receiver_queue_list is the list of queues to
        # which this message is copied.
        receiver_queue_list = output_queues_list[stream_index]
        # output_streams[stream_index] is the output stream
        # on which this message arrived.
        # output_stream_name is the name of the stream on which
        # this message arrived.
        output_stream_name = output_streams[stream_index].name

        # The messages in the queue must be serializable. The
        # object _close is not serializable; so convert it into a
        # string '_close'. The receiving agent will convert this  
        # string back into the object _close.
        if message_content is _close:
            message_content = '_close'
        # The message placed in each of the receiver queues is
        # a tuple (name of the stream, content of the message).
        message = (output_stream_name, message_content)

        for receiver_queue in receiver_queue_list:
            #print 'In MakeOutputManager. receiver_queue =', receiver_queue
            try:
                receiver_queue.put(message)
                print 'put message = ', message
            except Exception, err:
                print 'Error', err
                return

        return _no_value

    # Create the agent
    stream_agent(
        # The agent listens to output streams of func
        inputs=output_streams,
        # The agent does not generate its own output streams.
        outputs=[Stream('empty_stream')],
        # The agent processes messages from all its input
        # streams as the messages arrive. The agent does not
        # synchronize messages across different input streams.
        # So, f_type is 'asynch_element' rather than 'element'.
        f_type='asynch_element',
        f=send_message_to_queue)


def make_process(
        input_stream_names, output_stream_names, func,
        input_queue, output_queues_list):
    """ Makes a process that gets messages on its single
    input queue, processes the messages and puts messages
    on its output queues. An output queue of this process
    is an input queue of another process.
    
    Parameters
    ----------
    input_stream_names : list of str
             List of names of input streams
    output_stream_names : list of str
             List of names of output streams
    func : function
           The parameters of func are
                input_streams, output_streams where
            input_streams is a list of streams whose names
            are in input_stream_names and where
            output_streams is a list of streams whose names
            are in output_stream_names. func gets messages
            on its input streams and puts messages on its
            output streams.
    input_queue: multiprocessing.Queue
            Each process has a single input queue along
            which it receives messages.
    output_queues_list : list of list of multiprocessing.Queue
            output_queues_list[j] is the list of queues to
            which messages that appear on the stream with name
            output_stream_names[j] should be sent.

    Returns
    -------
          None
    Attributes
    ----------
    input_streams : list of Stream
           input_stream[j] is the Stream with name
           input_stream_name[j].
    output_streams : list of Stream
           output_stream[j] is the Stream with name
           output_stream_name[j].
    map_name_to_input_stream : dict
           key : str
                 name of an input stream
           value : Stream
                 The stream with the specified name.
    
    Notes
    -----
    make_process carries out the following steps:
    (1) Sets up data structures for the next two steps.
    (2) Calls func which creates the network of agents
    that process messages on its input streams and puts
    messages on its output streams.
    (3) Makes the output and input managers.
                

    """
    print 'input_queue', input_queue
    print 'output_queues_list', output_queues_list
    print 'input_stream_names', input_stream_names
    print 'output_stream_names', output_stream_names

    # Create input_streams, output_streams and
    # map_name_to_input_stream
    input_streams = [Stream(name) for name in input_stream_names]
    output_streams = [Stream(name) for name in output_stream_names]
    map_name_to_input_stream = dict()
    for stream in input_streams:
        map_name_to_input_stream[stream.name] = stream
    # Call the function that creates a network of agents that
    # map input streams to output streams.
    func(input_streams, output_streams)

    make_output_manager(output_streams, output_queues_list)
    make_input_manager(input_queue, input_streams, map_name_to_input_stream)


def main():
    def simple(input_streams, output_streams):
        for i in range(5):
            output_streams[0].append(i*10)
            time.sleep(0.1)
        output_streams[0].append(_close)

    
    def double_agent(input_streams, output_streams):
        input_stream = input_streams[0]
        output_stream = output_streams[0]
        
        def double(v):
            return 2*v
        
        return stream_agent(
            inputs=input_stream,
            outputs=output_stream,
            f_type='element',
            f=double)

    def print_agent(input_streams, output_streams):
        input_stream = input_streams[0]
        
        def p(v):
            pass
            #print 'print_agent', input_stream.name, v

        
        return stream_agent(
            inputs=input_stream,
            outputs=[],
            f_type='element',
            f=p)

    #queue_0 = None
    queue_2 = Queue()

    SERVER = 'pcbunn.cacr.caltech.edu'
    PORT = 61613
    DESTINATION='topic/remote_queue_new'
    #queue_1 = RemoteQueue(SERVER, PORT, DESTINATION)

    process_0 = Process(target=make_process,
                        args= (
                            [], # list of input stream names
                            ['s'], # list of output stream names
                            simple, # func
                            None, # the input queue
                            #[[(SERVER, PORT, DESTINATION)]] # list of list of output queues
                            [[queue_2]]
                            ))

    ## process_1 = Process(target=make_process,
    ##                     args= (
    ##                         ['simple_stream'], # list of input stream names
    ##                         ['double_stream'], # list of output stream names
    ##                         double_agent, # func
    ##                         queue_1, # the input queue
    ##                         [[queue_2]] list of list of output queues
    ##                         ))

    process_2 = Process(target=make_process,
                        args= (
                            ['s'], # list of input stream names
                            [], # list of output stream names
                            print_agent, # func
                            #(SERVER, PORT, DESTINATION), # the input queue
                            queue_2,
                            [] # list of list of output queues
                            ))

    print 'starting process_0'
    #process_1.start()
    process_0.start()
    #process_1.join()
    
    #time.sleep(1.0)
                               
    process_2.start()
    
    process_0.join()
    process_2.join()
    
    



if __name__ == '__main__':
    main()

            
                
    
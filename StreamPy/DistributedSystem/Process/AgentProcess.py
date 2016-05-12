import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from Stream import Stream, _close, _no_value
from Operators import stream_agent
from multiprocessing import Process, Queue
import threading
import json
from ProcessServer import create_server_thread
import logging

logging.basicConfig(filename="Logs/make_process_log.log", filemode='w', level=logging.INFO)

class AgentProcess():

    def __init__(self, id, name, input_stream_names, output_stream_names, func, output_process_list):
        self.id = id
        self.name = name
        self.input_stream_names = input_stream_names
        self.output_stream_names = output_stream_names
        self.func = func
        self.output_process_list = output_process_list
        self.process_conns = {}

    def run(self):
        logging.info("Running process {1} on {1}:{2}".format(self.name, self.host, self.port))
        self.finished_execution = False
        self.wait = True
        create_server_thread(self.host, self.port, self.input_queue, self.finished_execution)
        logging.info("Server created. Listening on {0}:{1}".format(self.host, self.port))

        threading.Thread(target=self.runCommands).start()

        self.input_streams = [Stream(name) for name in self.input_stream_names]
        self.output_streams = [Stream(name) for name in self.output_stream_names]
        self.map_name_to_input_stream = dict()
        for stream in self.input_streams:
            self.map_name_to_input_stream[stream.name] = stream
        # Call the function that creates a network of agents that
        # map input streams to output streams.

        while self.wait:
            pass

        self.func(self.input_streams, self.output_streams)

        self.make_output_manager()
        self.make_input_manager()
        for id in self.process_conns:
            self.process_conns[id].close()
            print "Deleted socket for process {0}".format(id)
        self.node.remove_process(self.id)

    def runCommands(self):
        while True:
            message = self.command_queue.get()
            if message == 'start':
                self.wait = False

    def start(self, host, port, input_queue, command_queue, node):
        self.host = host
        self.port = port
        self.input_queue = input_queue
        self.command_queue = command_queue
        self.node = node
        self.process = Process(target=self.run,
                            args=())
        self.process.start()
    def join(self):
        self.process.join()

    def make_input_manager(self):
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
        # If the process has no input queue, i.e., if
        # the process is a source, then the process
        # has nothing to do. In this case, set
        # finished_execution to True.
        if len(self.input_streams) == 0:
            self.finished_execution = True

        while not self.finished_execution:
            try:
                message = self.input_queue.get()
                print "Process {0} received message {1}".format(self.id, message)
                message = json.loads(message)
                logging.info('make_input_manager, message = ' + str(message))
            except Exception, err:
                print err
                print "Error"
                logging.error(err)
                return
            # This message_content is to be appended to the
            # stream with name stream_name.
            #print 'received message: ', message
            stream_name, message_content = message
            # Get the input_stream to which the message must
            # be appended.
            # print stream_name, self.id
            input_stream = self.map_name_to_input_stream[stream_name]
            # print stream_name, input_stream, self.id
            # Message arrived for a closed stream. Error!
            if input_stream.closed:
                logging.warning('inserting values into a closed stream!')
                return

            # Append message_content to input_stream. Note message_content
            # may be '_close'; in this case convert the message content to
            # the object _close. This is because the string '_close' was
            # used as a proxy for the object _close because strings can be
            # serialized.
            if message_content == '_close':
                message_content = _close
            # print "Appending message to stream"
            input_stream.append(message_content)

            # Terminate execution of the input manager when all its
            # input streams get closed.
            if message_content == _close:
                input_stream.close()
                self.finished_execution = \
                  all([stream.closed for stream in
                       self.map_name_to_input_stream.values()])

    def make_output_manager(self):
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
            receiver_process_list = self.output_process_list[stream_index]
            # output_streams[stream_index] is the output stream
            # on which this message arrived.
            # output_stream_name is the name of the stream on which
            # this message arrived.
            output_stream_name = self.output_streams[stream_index].name

            # The messages in the queue must be serializable. The
            # object _close is not serializable; so convert it into a
            # string '_close'. The receiving agent will convert this
            # string back into the object _close.
            if message_content is _close:
                message_content = '_close'
            # The message placed in each of the receiver queues is
            # a tuple (name of the stream, content of the message).
            message = json.dumps((output_stream_name, message_content))

            for process_id in receiver_process_list:
                if process_id not in self.process_conns:
                    self.process_conns[process_id] = self.node.create_process_conn(process_id)
                # print "Process {0} sending message {1} to process {2}".format(self.id, message, process_id)
                self.process_conns[process_id].send(message)
                # self.process_conns[process_id].close()
                # del self.process_conns[process_id]
                # print "Success!"

            return _no_value

        # Create the agent
        stream_agent(
            # The agent listens to output streams of func
            inputs=self.output_streams,
            # The agent does not generate its own output streams.
            outputs=[Stream('empty_stream')],
            # The agent processes messages from all its input
            # streams as the messages arrive. The agent does not
            # synchronize messages across different input streams.
            # So, f_type is 'asynch_element' rather than 'element'.
            f_type='asynch_element',
            f=send_message_to_queue)


def main():
    #########################################
    # 1. DEFINE ELEMENT FUNCTIONS
    # The signature for all these functions is
    # f(input_streams, output_streams) where
    # input_streams and output_streams are lists of
    # Stream.

    # Generate a stream with N random numbers and
    # then close the stream.
    N = 5
    from random import randint
    def random_ints(input_streams, output_streams):
        # Append random numbers to output_streams[0]
        # The numbers are in the interval (0, 99).
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
    def f(v): return 2*v
    def apply_func_agent(input_streams, output_streams):
        input_stream = input_streams[0]
        output_stream = output_streams[0]

        def apply_func(v):
            # When the input stream is closed, return
            # _close to cause the output stream to close.
            if v == _close:
                return _close
            else:
                return f(v)

        return stream_agent(
            inputs=input_stream,
            outputs=output_stream,
            f_type='element',
            f=apply_func)

    # Print the values received on the input stream.
    def print_agent(input_streams, output_streams):
        input_stream = input_streams[0]

        def p(v):
            if v != _close:
                print 'print_agent', input_stream.name, v

        return stream_agent(
            inputs=input_stream,
            outputs=[],
            f_type='element',
            f=p)

    #########################################
    # 2. CREATE QUEUES

    #queue_0 = None
    conn_0 = ('localhost', 8891)
    queue_1 = Queue() # Input queue for process_1
    conn_1 = ('localhost', 8892)
    #queue_2 = Queue() # Input queue for process_2
    queue_2 = Queue()
    conn_2 = ('localhost', 8893)

    #########################################
    # 2. CREATE PROCESSES

    # This process is a source; it has no input queue
    # This process sends simple_stream to queue_1
    process_0 = AgentProcess(id=0,
                             input_stream_names=[],
                             output_stream_names=['random_ints_stream'],
                             func=random_ints,
                             output_conn_list=[[conn_1]])

    # This process receives simple_stream from process_0.
    # It sends double_stream to process_2.
    # It receives messages on queue_1 and sends messages to queue_2.

    process_1 = AgentProcess(id=1,
                             input_stream_names=['random_ints_stream'],
                             output_stream_names=['func_stream'],
                             func=apply_func_agent,
                             output_conn_list=[[conn_2]])


    # This process is a sink; it has no output queue.
    # This process receives double_stream from process_1.
    # It prints the messages it receives.
    # This process prints [0, 2, ... , 8]

    process_2 = AgentProcess(id=2,
                             input_stream_names=['func_stream'],
                             output_stream_names=[],
                             func=print_agent,
                             output_conn_list=[])


    #########################################

    # 3. START PROCESSES
    x = Queue()
    y = Queue()
    z = Queue()
    process_2.start(conn_2[0], conn_2[1], x)
    #time.sleep(0.1)
    process_1.start(conn_1[0], conn_1[1], y)
    #time.sleep(0.1)
    process_0.start(conn_0[0], conn_0[1], z)

    z.put('start')
    y.put('start')
    x.put('start')

    #########################################
    # 4. JOIN PROCESSES
    #time.sleep(0.1)
    process_2.join()
    #time.sleep(0.1)
    process_1.join()
    #time.sleep(0.1)
    process_0.join()



if __name__ == '__main__':
    main()

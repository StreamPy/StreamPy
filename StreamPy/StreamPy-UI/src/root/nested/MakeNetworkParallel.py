from Stream import Stream
from Stream import _no_value, _multivalue
from Agent import Agent
#from OperatorsTestParallel import stream_agent
import OperatorsTestParallel
from Operators import stream_agent
import OperatorsTestParallel

def make_network(stream_names_tuple, agent_descriptor_dict):
    """ This function makes a network of agents given the names
    of the streams in the network and a description of the
    agents in the network.

    Parameters
    ----------
    stream_names_tuple: tuple of str
        A tuple consisting of names of streams in the network.
        Each stream in the network must have a unique name.
    agent_descriptor_dict: dict of tuples
        The key is an agent name
        The value is a tuple:
           in_list, out_list, f, f_type, f_args, state,
           call_streams
           where:
             in_list: list of input stream names
             out_list: list of output stream names
             f: function associated with the agent
             f_type: 'element', 'list', 'window', etc
             f_args: tuple of arguments for functions f
             state: the state associated with this agent
             call_streams: list of names of call streams.

    Returns
    ---------------
    stream_dict: dict
          key: stream name
          value: Stream
    agent_dict: dict
          key: agent name
          value: agent with the specified description:
                 in_list, out_list, f, f_type, f_args, state,
                 call_streams=[timer_stream]
                 where one timer stream is associated with
                 each agent.

    """
    # Create streams and insert streams into stream_dict.
    stream_dict = dict()
    for stream_name in stream_names_tuple:
        stream_dict[stream_name] = Stream(stream_name)

    ## # Only for debugging
    ## for key, value in stream_dict.items():
    ##     print 'stream_name: ', key
    ##     print 'stream:', value
    
    # Create agents with the specified description
    # and put the agents into agent_dict.
    agent_dict = dict()
    for agent_name in agent_descriptor_dict.keys():
        #print 'agent_name:', agent_name
        #print agent_descriptor_dict[agent_name]
        
        in_list, out_list, f, f_type, f_args, state, call_list = \
          agent_descriptor_dict[agent_name]

        ## # Only for debugging
        ## print 'in_list', in_list
        ## print 'out_list', out_list
        ## print 'f', f
        ## print 'f_args', f_args
        ## print 'f_type', f_type
        ## print 'state', state

        # inputs is either a single stream or a list of streams.
        # (Note: inputs is not a list of NAMES of streams).
        # If in_list consists of a single stream
        # then inputs is a single stream, otherwise it is a
        # list of streams.
        if len(in_list) == 1:
            single_input_stream_name = in_list[0]
            inputs = stream_dict[single_input_stream_name]
        else:
            inputs = list()
            for input_stream_name in in_list:
                inputs.append(stream_dict[input_stream_name])

        # outputs is either a single stream or a list of streams.
        # (Note: outputs is not a list of NAMES of streams).
        # If out_list consists of a single output stream
        # then outputs is a single stream, otherwise it is a
        # list of streams.
        if len(out_list) == 1:
            single_output_stream_name = out_list[0]
            outputs = stream_dict[single_output_stream_name]
        else:
            outputs = list()
            for output_stream_name in out_list:
                outputs.append(stream_dict[output_stream_name])

        call_streams = list()
        if call_list is None:
            call_list = list()
        for call_stream_name in call_list:
            print '------------stream_dict=----------'
            print stream_dict
            call_streams.append(stream_dict[call_stream_name])

        # Create agents and insert them into agent_dict
        agent_dict[agent_name] = OperatorsTestParallel.stream_agent(
            inputs, outputs, f_type, f, f_args, state, call_streams)
        
        
        # Set the name for this agent.
        agent_dict[agent_name].name = agent_name

    return (stream_dict, agent_dict)

def make_timer_streams_for_network(agent_dict):
    """
    Returns
    -------
    agent_timer_dict, a dict where
    key: agent_name
    value: a stream (note a stream and not a name)
       This stream is a call stream of the agent
       with the specified name (the key). Usually,
       timing messages are sent on this stream.
       The agent takes a step when it receives a
       message on this stream.

    """
    agent_timer_dict = dict()
    for agent_name, agent in agent_dict.items():
        timer_stream = Stream(agent_name + ':timer')
        if agent.call_streams is None:
            agent.call_streams = [timer_stream]
        agent_timer_dict[agent_name] = timer_stream
    return agent_timer_dict

def network_data_structures(stream_names_tuple, agent_descriptor_dict):
    """Builds data structures for the network. These data
    structures are helpful for animating the network and
    for building networks of processes.

    Parameters
    ----------
       Same as for make_network.

    Return Values
    -------------
       (stream_to_agent_list_dict,
       agent_to_stream_dict,
       agent_to_agent_list_dict)
       
       stream_to_agent_list_dict
          key: stream_name
          value: list of agent_name.
          The stream with name stream_name (the key)
          is an input stream of each agent
          whose name is in the list (the value).
          For example if key is 's' and value is
          ['u', 'v', 'w'] then the stream with name 's'
          is an input stream of the agents with names
          'u', 'v', and 'w'.

       agent_to_stream_dict
           key: stream_name
           value: str. A single agent_name.
           The stream with name stream_name (the key)
           is the unique output stream of the agent
           with name agent_name (the value). For example,
           if a key is 's' and the corresponding value
           is 'a', then the stream with name 's' is
           generated by the agent with name 'a'.

       agent_to_agent_list_dict
           key: agent_name
           value: list of agent names
           The agent with name agent_name (the key) has an
           output stream to each agent whose name is in value.
           
       agent_from_agent_list_dict
           key: agent_name
           value: list of agent names
           The agent with name agent_name (the key) has an
           input stream from each agent whose name is in value.

    
    
    """
    stream_to_agent_list_dict = dict()
    for stream_name in stream_names_tuple:
        stream_to_agent_list_dict[stream_name] = list()
    
    agent_to_stream_dict = dict()

    # Construct stream_to_agent_list_dict and agent_to_stream_dict
    # from agent_descriptor_dict
    for agent_name, descriptor in agent_descriptor_dict.iteritems():
        input_stream_list = descriptor[0]
        output_stream_list = descriptor[1]
        for stream_name in input_stream_list:
            stream_to_agent_list_dict[stream_name].append(agent_name)
        for stream_name in output_stream_list:
            if stream_name in agent_to_stream_dict:
                raise Exception(
                    stream_name+'output by'+agent_to_stream_dict[stream_name]+'and'+agent_name)
            agent_to_stream_dict[stream_name] = agent_name

    # Construct agent_to_agent_list_dict from
    # agent_descriptor_dict, stream_to_agent_list_dict, and
    # agent_to_stream_dict.
    agent_to_agent_list_dict = dict()
    # Initialize agent_to_agent_list_dict
    for agent_name in agent_descriptor_dict.keys():
        agent_to_agent_list_dict[agent_name] = list()
    # Compute agent_to_agent_list_dict
    # If a stream is output of agent x and input to agents y, z
    # then agent x outputs to [y,z]
    for stream_name, agent_name in agent_to_stream_dict.iteritems():
        agent_to_agent_list_dict[agent_name].extend(
            stream_to_agent_list_dict[stream_name])

    # Construct agent_from_agent_list_dict from
    # agent_descriptor_dict, stream_to_agent_list_dict, and
    # agent_to_stream_dict.
    agent_from_agent_list_dict = dict()
    # Initialize agent_from_agent_list_dict
    for agent_name in agent_descriptor_dict.keys():
        agent_from_agent_list_dict[agent_name] = list()
    # Compute agent_from_agent_list_dict
    # If a stream is an input of agent x and is an output of agents y, z
    # then agents[y,z] output to agent x.
    for stream_name, agent_name_list in stream_to_agent_list_dict.iteritems():
        for receiving_agent_name in agent_name_list:
            agent_from_agent_list_dict[receiving_agent_name].append(
                agent_to_stream_dict[stream_name])

    return (stream_to_agent_list_dict, agent_to_stream_dict,
            agent_to_agent_list_dict, agent_from_agent_list_dict) 


def main():
    # STEP 1
    # PROVIDE CODE OR IMPORT PURE (NON-STREAM) FUNCTIONS
    
    from random import randint
    def rand(f_args):
        max_integer = f_args[0]
        return randint(0, max_integer)

    def split(m, f_args):
        divisor = f_args[0]
        return [_no_value, m] if m%divisor else [m, _no_value]

    def print_value(v, index):
            #print name + '[' , index , '] = ', v
            print '[' , index , '] = ', v
            return (index+1)

    # STEP 2
    # SPECIFY THE NETWORK.
    
    # Specify names of all the streams.
    stream_names_tuple = (
        'random_stream', 'multiples_stream', 'non_multiples_stream',
        'generate_random_timer')

    # Specify the agents:
    # key: agent name
    # value: list of input streams, list of output streams, function, function type,
    #        tuple of arguments, state
    agent_descriptor_dict = {
        'generate_random': [
            [], ['random_stream'], rand, 'element', (100,), None, ['generate_random_timer']],
        'split': [
            ['random_stream'], ['multiples_stream', 'non_multiples_stream'],
            split, 'element', (2,), None, None],
        'print_random': [
            ['random_stream'], [], print_value, 'element', None, 0, None],
        'print_multiples': [['multiples_stream'], [], print_value, 'element', None, 0, None],
        'print_non_multiples': [['non_multiples_stream'], [], print_value, 'element', None, 0, None]
        }

    # STEP 3: MAKE THE NETWORK
    stream_dict, agent_dict = make_network(
        stream_names_tuple, agent_descriptor_dict)
    agent_timer_dict = make_timer_streams_for_network(agent_dict)

    # STEP 3B: GET DATA STRUCTURES OF THE NETWORK
    (stream_to_agent_list_dict, agent_to_stream_dict,
     agent_to_agent_list_dict, agent_from_agent_list_dict) = \
       network_data_structures(stream_names_tuple, agent_descriptor_dict)

    ## # Only for debugging
    ## for key, value in stream_to_agent_list_dict.iteritems():
    ##     print 'stream_to_agent_list_dict key: ', key
    ##     print 'stream_to_agent_list_dict value: ', value

    ## for key, value in agent_to_stream_dict.iteritems():
    ##     print 'agent_to_stream_dict key: ', key
    ##     print 'agent_to_stream_dict value: ', value

    ## for key, value in agent_to_agent_list_dict.iteritems():
    ##     print 'agent_to_agent_list_dict key: ', key
    ##     print 'agent_to_agent_list_dict value: ', value

    ## for key, value in s_dict.items():
    ##     print 'stream name', key
    ##     print 'stream', value

    ## for key, value in a_dict.items():
    ##     print 'agent name', key
    ##     print 'agent', value

    ## for key, value in agent_timer_dict.items():
    ##     print 'timer name is', key
    ##     print 'timer', value

    
    # STEP 4: DRIVE THE NETWORK BY APPENDING
    #      VALUES TO TIMER STREAMS
    
    for t in range(5):
        print
        print '--------- time step: ', t
        # Append t to each of the timer streams
        for agent_name, timer_stream in agent_timer_dict.iteritems():
            print
            print 'Execute single step of agent with name', agent_name
            timer_stream.append(t)
            
            ## # for debugging
            ## for stream in stream_dict.values():
            ##     stream.print_recent()

            for receiving_agent_name in agent_to_agent_list_dict[agent_name]:
                descriptor = agent_descriptor_dict[receiving_agent_name]
                receiving_agent = agent_dict[receiving_agent_name]
                input_stream_list = descriptor[0]
                for stream_name in input_stream_list:
                    stream = stream_dict[stream_name]
                    print 'from', agent_name, 'on', stream_name, 'to', receiving_agent_name,
                    print stream.recent[stream.start[receiving_agent]:stream.stop]

            descriptor = agent_descriptor_dict[agent_name]
            agent = agent_dict[agent_name]
            input_stream_list = descriptor[0]
            for stream_name in input_stream_list:
                stream = stream_dict[stream_name]
                sending_agent_name = agent_to_stream_dict[stream_name]
                print 'from', sending_agent_name, 'on', stream_name, 'to', agent_name,
                print stream.recent[stream.start[agent]:stream.stop]


            ## # Print messages in transit to the input port
            ## # of each agent.
            ## for agent_name, agent in agent_dict.iteritems():
            ##     descriptor = agent_descriptor_dict[agent_name]
            ##     input_stream_list = descriptor[0]
            ##     for stream_name in input_stream_list:
            ##         stream = stream_dict[stream_name]
            ##         print "messages in ", stream_name, "to", agent.name
            ##         print stream.recent[stream.start[agent]:stream.stop]


if __name__ == '__main__':
    main()


    
    

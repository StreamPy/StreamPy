'''
Handle JSON <--> agent descriptor dict -> Streams network
'''

import re
import json
from pprint import pprint

from Stream import Stream
from Stream import _no_value, _multivalue
from Agent import Agent
from Operators import stream_agent

from helper import *
from components import *


def make_network(stream_names_tuple, agent_descriptor_dict):
    """ This function makes a network of agents given the names
    of the streams in the network and a description of the
    agents in the network.

    Parameters
    ----------
    stream_names_tuple: tuple of lists
        A tuple consisting of names of streams in the network.
        Each stream in the network must have a unique name.
    agent_descriptor_dict: dict of tuples
        The key is an agent name
        The value is a tuple:
           in_list, out_list, f, f_type, f_args, state
           where:
             in_list: list of input stream names
             out_list: list of output stream names
             f: function associated with the agent
             f_type: 'element', 'list', 'window', etc
             f_args: tuple of arguments for functions f
             state: the state associated with this agent.

    Local Variables
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
    agent_timer_dict: dict
          key: agent_name
          value: Stream
          The value is the timer stream associated with the
          agent. When the timer stream has a message, the
          agent is made to execute a step.

    """
    # Create streams and insert streams into stream_dict.
    stream_dict = dict()
    for stream_name in stream_names_tuple:
        stream_dict[stream_name] = Stream(stream_name)

    agent_dict = dict()
    agent_timer_dict = dict()

    # Create agents with the specified description
    # and put the agents into agent_dict.
    for agent_name in agent_descriptor_dict.keys():
        in_list, out_list, f, f_type, f_args, state, call_streams = \
          agent_descriptor_dict[agent_name]

        # Replace a list consisting of a single input stream
        # by the stream itself.
        if len(in_list) == 1:
            single_input_stream_name = in_list[0]
            inputs = stream_dict[single_input_stream_name]
        else:
            inputs = list()
            for input_stream_name in in_list:
                inputs.append(stream_dict[input_stream_name])

        # Replace a list consisting of a single output stream
        # by the stream itself.
        if len(out_list) == 1:
            single_output_stream_name = out_list[0]
            outputs = stream_dict[single_output_stream_name]
        else:
            outputs = list()
            for output_stream_name in out_list:
                outputs.append(stream_dict[output_stream_name])
        
        # Create timer streams and insert them into agent_timer_dict 
        agent_timer_dict[agent_name] = Stream(
            agent_name + ':timer')

        # Create agents and insert them into agent_dict
        agent_dict[agent_name] = stream_agent(
            inputs, outputs, f_type, f, f_args, state,
            call_streams=[agent_timer_dict[agent_name]])

        # Set the name for this agent.
        agent_dict[agent_name].name = agent_name

    return (stream_dict, agent_dict, agent_timer_dict)


# This goes from Flowhub's JSON to our JSON    
# key: agent name
# value: list of input streams, list of output streams, function, function type,
#        tuple of arguments, state
# Eg. 'generate_random': [
#            [], ['random_stream'], rand, 'element', (100,), None],
def make_agent_descriptor_dict(instance_dict, comp_list):
    dic = {}
    json_dic = {}
    # TODO: find a better way to do this
    # Currently a hard-coded string-to-function_object dict 
    f_dict = {'generate_of_random_integers': generate_of_random_integers, 
              'split_into_even_odd': split_into_even_odd, 
              'print_value': print_value, 
              'multiply_elements': multiply_elements,
              'split': split,
              'make_rectangles': make_rectangles,
              'make_circles': make_circles,
              'make_triangles': make_triangles,
              'consecutive_ints': consecutive_ints,
              'show': show
              }

    for stream in instance_dict:
        s_name, s_id = clean_id(stream.split('/')[1])
        s_name = name_with_new_id(comp_list, s_name, s_id)
        dic[s_name] = [0, 0, 0, 0, 0, 0]
        json_dic[s_name] = []
        
        state = None
        func = str()
        type = 'element'
        param = ()
        
        # (Default function name: component name with "_stream" removed)
        # Get rid of the instance id (ie. 0, 1, 2...) to get function name
        func = s_name.replace('_stream', '')
        m = re.search(r'\d+$', func)
        if m is not None:
            func = func.replace(m.group(), '')
        
        input = []
        for i in instance_dict[stream]['in']:
            if '=' not in i:
                src_name_id, src_port = clean_id(i.split('/')[1])
                src_name, src_id = clean_id(src_name_id)
                
                src_name = name_with_new_id(comp_list, src_name, src_id)
                input.append(src_name + '_PORT_' + src_port)
                
            else:
                data_name = i.split('=')[0]
                data_val = cast(i.split('=')[1])
                if data_name == 'state':
                    state = data_val
                elif data_name == 'type':
                    type = data_val
                elif data_name == 'func':
                    func = data_val
                else:
                    param = param + (data_val,)
                    
        output = []
        for i in instance_dict[stream]['out']:
            src_name_id, src_port = clean_id(i.split('/')[1])
            src_name, src_id = clean_id(src_name_id)

            src_name = name_with_new_id(comp_list, src_name, src_id)

            output.append(src_name + '_PORT_' + src_port)
        
        if param == ():
            param = None
        

        dic[s_name][0] = input
        dic[s_name][1] = output
        dic[s_name][2] = func
        dic[s_name][3] = type
        dic[s_name][4] = param
        dic[s_name][5] = state

        json_dic[s_name] = [input, output, func, type, param, state]

    json_dic = json.dumps(json_dic, sort_keys=True, 
                              indent=4, separators=(',', ': '))    

    return json_dic



# Make stream_names_tuple from Flowhub's JSON
# Returns the JSON str equivalent of stream_names_tuple
def make_stream_names_tuple(instance_dict, comp_list):
    stream_names_tuple = ()
    for comp in instance_dict:
        for i in instance_dict[comp]['in']:

            # For input streams (not parameters)
            if '=' not in i:
                #Replace random id with 0, 1, 2...
                src_name_id, src_port = clean_id(i.split('/')[1])
                src_name, src_id = clean_id(src_name_id)
    
                src_name = name_with_new_id(comp_list, src_name, src_id)
    
                s = src_name + '_PORT_' + src_port
                if s not in stream_names_tuple:
                    stream_names_tuple = stream_names_tuple + (s,)

        for i in instance_dict[comp]['out']:

            #Replace random id with 0, 1, 2...
            src_name_id, src_port = clean_id(i.split('/')[1])
            src_name, src_id = clean_id(src_name_id)

            src_name = name_with_new_id(comp_list, src_name, src_id)

            s = src_name + '_PORT_' + src_port

            if s not in stream_names_tuple:
                stream_names_tuple = stream_names_tuple + (s,)
    
    stream_names_tuple_json = json.dumps(stream_names_tuple, sort_keys=True, 
                              indent=4, separators=(',', ': '))
    return stream_names_tuple_json

# Grab JSON in my special format and turn into dict to execute
def JSON_to_descriptor_dict_and_stream_names(my_json_file_name):
    # Import json file
    with open(my_json_file_name) as data_file:    
        json_data = json.load(data_file)
    
    # Convert str to objects
    agent_descriptor_dict = json_data['agent_descriptor_dict']
    copy = json_data['agent_descriptor_dict']
    
    # TODO: find a better way to do this
    # Currently a hard-coded string-to-function_object dict 
    f_dict = f_dict = {'generate_of_random_integers': generate_of_random_integers, 
              'split_into_even_odd': split_into_even_odd, 
              'print_value': print_value, 
              'multiply_elements': multiply_elements,
              'split': split,
              'make_rectangles': make_rectangles,
              'make_circles': make_circles,
              'make_triangles': make_triangles,
              'consecutive_ints': consecutive_ints,
              'show': show
              }
    
    for agent in agent_descriptor_dict:
        
        ## func: str to function object
        func_str = agent_descriptor_dict[agent][2] 
        agent_descriptor_dict[agent][2] = f_dict[func_str]
        
        ## type: from unicode to str
        agent_descriptor_dict[agent][3] = str(agent_descriptor_dict[agent][3])
        
        ## param: array to tuple and str to None
        if type(agent_descriptor_dict[agent][4]) == list:
            tup = ()
            for i in agent_descriptor_dict[agent][4]:
                tup = tup + (i,)
            
            agent_descriptor_dict[agent][4] = tup
        elif agent_descriptor_dict[agent][4] == 'null' or \
        agent_descriptor_dict[agent][4] == 'None':
            agent_descriptor_dict[agent][4] = None
        
        ## state: str to None
        if agent_descriptor_dict[agent][5] == 'null' or \
        agent_descriptor_dict[agent][5] == 'None':
            agent_descriptor_dict[agent][5] = None
        
        ## Add last value, "call_streams"
        agent_descriptor_dict[agent].append([])
            
        copy[agent] = agent_descriptor_dict[str(agent)]
        
    return copy, json_data['stream_names_tuple']
    
def make_my_JSON(instance_dict, comp_list, json_data):

    stream_names_tuple = make_stream_names_tuple(instance_dict, comp_list)
    agent_descriptor_dict = make_agent_descriptor_dict(instance_dict, comp_list)    
    
    if json_data['groups']: # for graphs with groups
        groups = {}
        for group in json_data['groups']:
            
            group_name = group['name']
            nodes = []
            for node in group['nodes']:
                # Rename node
                label, id = clean_id(node.split('/')[1])

                if comp_list[label].index(id) == 0:
                    new_id = ''
                else:
                    new_id = str(comp_list[label].index(id))
                
                new_name = label + new_id
                nodes.append(new_name)
            # Add group data to the dict 'groups'
            groups[group_name] = nodes
            
        groups = str(groups)
        groups = groups.replace('\'', '\"').replace('u\"', '\"')
        
    else:
        groups = None

    inports = 'inports'
    outports = 'outports'
    # if there are exposed inports
    def get_exposed_ports(in_ports):
        str_name = str(in_ports)
        if len(json_data[str_name].keys()) > 0:
            ports = json_data[str_name]
            ## Start renaming
            # Make new dict
            output = {}
            # Rename node
            for s in ports:
                node = ports[s]['process']
                label, id = clean_id(node.split('/')[1])
                if comp_list[label].index(id) == 0:
                    new_id = ''
                else:
                    new_id = str(comp_list[label].index(id))
                
                new_sname = label + new_id + '_PORT_' + ports[s]['port']
                
                # Save cleaned name to dict
                output[s] = new_sname
            
            in_ports = str(output)
            in_ports = in_ports.replace('\'', '\"').replace('u\"', '\"')
        else:
            in_ports = '{}'
        return in_ports
    
    inports = get_exposed_ports(inports)
    outports = get_exposed_ports(outports)
    
    output_file_name = 'agent_descriptor.json'
    f = open(output_file_name, 'w')
    f.write('{\n')
    
    f.write('\"agent_descriptor_dict\":\n')
    f.write(agent_descriptor_dict)
    f.write(',\n')
    
    f.write('\"stream_names_tuple\":\n')
    f.write(stream_names_tuple)
    
    if groups:
        f.write(',\n')
        f.write('\"groups\":\n')
        f.write(groups)
    
    if inports:
        f.write(',\n')
        f.write('\"inports\":\n')
        f.write(inports)
    
    if outports:
        f.write(',\n')
        f.write('\"outports\":\n')
        f.write(outports)

    
    f.write('\n}')
    f.close()
    
    
    return output_file_name    



    
    

# from example.py

'''
rename_stream() replaces a component name
with the random id with an integer (1, 2, 3,...)
if there are multiple instances.

Parameters
----------
instance_dict : dict
    Component names with random id's paired with
    dict of it's 'in' and 'out' ports

Returns
-------
comp_list : dict
    Plain component name paired with list of id's
    associated with it

'''

def rename_stream(original_arr, comp_list):
    renamed_arr = []
    for i in original_arr:
        if '=' in i:
            # Then this is not a stream, but a data parameter
            renamed_arr.append(i)
        else:
            label_with_id, portname = clean_id(i.split('/')[1])
            label, id = clean_id(label_with_id)
            if comp_list[label].index(id) == 0:
                new_id = ''
            else:
                new_id = '_' + str(comp_list[label].index(id))
            renamed_arr.\
            append(label + new_id + '_PORT_' + portname)
    return renamed_arr



# Helper function to delete 'browser...'
def delete_startswith_substring(s, substring):
    if s.startswith(substring):
        return s[len(substring):]
    else:
        return s

def make_conn_dict(conn):
    conn_dict = {}
    for i in conn:
        if 'src' in i.keys():
            name = str(i['src']['process'])[x:]
            conn_dict[name] = []

    for i in conn:
        if 'src' in i.keys():
            src_name = str(i['src']['process'])[x:]
            tgt_name = str(i['tgt']['process'])[x:]
            port_name = str(i['src']['port'])
            conn_dict[src_name].append({'tgt': tgt_name , 'port': port_name})

    return conn_dict


## Dictionary of each component with it's input and output ports
## Ex. {process: {'in':[input_ports], 'out':[output_ports]}
def make_comps(data):
    # con_dict has the keys: src & tgt, vals: dict of process & port
    conn_list = data["connections"]

    ## Get list of unique output ports {port, process}
    out_ports = []
    for con_dict in conn_list:
        if 'src' in con_dict.keys() and con_dict['src'] not in out_ports:
            out_ports.append(con_dict['src'])


    ## Get list of unique input ports {port, process}
    in_ports = []
    for con_dict in conn_list:
        if con_dict['tgt'] not in in_ports:
            in_ports.append(con_dict['tgt'])


    ## Start constructing comps:
    ## {process: {'in':[input_ports], 'out':[output_ports]}
    comps = {}
    comp_list = data["processes"]
    for comp_dict in comp_list:
        if comp_list[comp_dict]['component'] not in comps:
            comps[comp_list[comp_dict]['component']] = {"in":[], "out":[]}

    ## Assign output and input ports to each component in comps
    for comp in comps:
        for op in out_ports:
            instance_name = op["process"].encode('ascii','ignore')    #name of module with ID
            name = comp.encode('ascii','ignore')                      #name of module

            if instance_name.find(name) == 0 and (op["port"] not in comps[comp]["out"]):
                comps[comp]["out"].append(op["port"])

        for ip in in_ports:
            instance_name = ip["process"].encode('ascii','ignore')    #name of module with ID
            name = comp.encode('ascii','ignore')                      #name of module

            if instance_name.find(name) == 0 and (ip["port"] not in comps[comp]["in"]):
                comps[comp]["in"].append(ip["port"])
    return comps


# From graph_to_program1.py

# (Not used when running Animation.py
# in favor of instant-execution/animation)
# Helps populate a .py output file.
# Returns 2 values:
# a sorted instance dict & a str of the function calls in order
def function_calls(instance_dict):

    function_string = str()
    
    # Make comp_list, a dictionary of each module and it's instance id's
    comp_list = make_comp_list(instance_dict)
    
    # Make a copy of instance_dict and call it
    # instance_dict_copy.
    # instance_dict_copy remains unchanged throughout
    # this program, while instance_dict changes as
    # nodes are deleted from the graph.
    instance_dict_copy = dict()
    
    
    for component, connections in instance_dict.items():        
        # populating instance_dict_copy with correctly formatted stream names
        connections_copy = dict()
        connections_copy['in'] = rename_stream(connections['in'], comp_list)
        connections_copy['out'] = rename_stream(connections['out'], comp_list)
        instance_dict_copy[component] = connections_copy

    # sorted_components will be the topological sort of
    # the graph
    sorted_components = list()

    # While nodes remain in the graph, do:
    while instance_dict:
        # sources is a list of sources (no inputs) in
        # the graph.
        sources = []
        # Go through instance_dict and append components
        # that have no inputs
        for component, connections in instance_dict.items():
            if not connections['in'] or \
            (len(connections['in']) == 1 and '=' in str(connections['in'])):
                sources.append(component)

        if not sources:
            print 'ERROR: GRAPH HAS CYCLES!'
            return

        for component_1 in sources:
            connections_1 = instance_dict[component_1]
            # outputs_1 is the list of outputs of component_1
            outputs_1 = connections_1['out']

            # for each output port, output_1, of
            # the source, component_1, do:
            for output_1 in outputs_1:
                # Inspect remaining graph and
                # delete output_1 from the inputs of each
                # node in the graph.
                for component_2, connections_2 in instance_dict.items():
                    inputs_2 = connections_2['in']
                    # If the output port, output_1, is an input then
                    # delete it from the input list of this component,
                    # i.e., component_2
                    if output_1 in inputs_2:
                        connections_2['in'] = \
                          [input_2 for input_2 in inputs_2 if input_2 != output_1]
                        instance_dict[component_2] = {
                            'in':connections_2['in'],
                            'out':connections_2['out']}

            # Add a 3-element list with the name of the component, its
            # inputs and its outputs to sorted_components.
            sorted_components.append([component_1,
                                      instance_dict_copy[component_1]['in'],
                                      instance_dict_copy[component_1]['out']]
                                      )
            # Deleted the source itself.
            del(instance_dict[component_1])

    # The graph is empty, and all the nodes have been sorted.

    # Cleaning the names of components and ports.
    for c in sorted_components:
        c[0] = c[0].split('/')[1]

        # output_string is something like:
        # 'output_1, output_2, output_3 = ' if there is at least one
        # output, and is the empty string if there is no output.
        output_string = str()
        # streams_string are the strings that name the streams
        # ie. stream_name.set_name('stream_name')
        streams_string = str()
        
        for o in c[2]:
            output_string = output_string + o + ', '
            streams_string = streams_string + o + '.set_name(\'' + o + '\')\n'
        # Delete the very last comma
        output_string = output_string[:-2]
        if output_string:
            output_string += ' = '

        # input_string is '()' if there are no inputs.
        # and otherwise it is like: (input_1, input_2, input_3)
        if not c[1]:
            input_string = ''
        else:
            input_string = str()
            
            for i in c[1]:
                input_string = input_string + i + ', '
            input_string = input_string[:-2]

        label, id = clean_id(c[0])
        ## statement is a function call in this format: 
        ## output_stream = component(input stream)
        statement = output_string + label + '(' + input_string + ')'

        ## Visualization data is the stream values at each component,
        ## so I'm adding a "write to file" line after each function call

        if '' == input_string:
            viz_call = ''
        else:
            viz_call = 'write_stream' + '(' + input_string.split(',')[0] + ')\n'
        
        function_string += statement +  '\n'
        function_string += streams_string

    return instance_dict_copy, function_string


# From examples.py

## (Not used anymore in favor of automatic execution/animation)
def ex(json_file_name):
    ## Open new file to write to
    output_file_name = 'pstreams_output.py'
    f = open(output_file_name, 'w')
    
    ## Import json file
    with open(json_file_name) as data_file:    
        data = json.load(data_file)

    ## Get list of unique components
    comps = make_comps(data)

    
    ## x is the length of the file name (aka the part we need to cut off)
    #x = len(comps.keys()[0].encode('ascii','ignore').split('/')[0]) + 1

    setup_template_file = open('setup_template_simple.txt', 'r')
    setup_template = [line.rstrip('\n') for line in setup_template_file] # convert file to array of lines
    
    ## Write setup imports, etc to file
    for line in setup_template:
            f.write(line + '\n')
            
    ## Create a Python function for each module and write it to file
    ## This is not used if we are importing functions that we already have
    
    #for c in comps:
    #    func_name = c.encode('ascii','ignore')[x:]
    #    
    #    in_streams = ''
    #    for ip in comps[c]['in']:
    #        in_streams = ip.encode('ascii','ignore') + ', ' + in_streams
    #    in_streams = in_streams[:-2]
    #    
    #    out_streams = ''
    #    for op in comps[c]['out']:
    #        out_streams = op.encode('ascii','ignore') + ', ' + out_streams
    #    out_streams = out_streams[:-2]
    #    
        
    #    for line in func_template:
    #        if len(in_streams) == 0:
    #            line = line.replace("IN_STREAM, OUT_STREAM", 'OUT_STREAM')
    #        if len(out_streams) == 0:
    #            line = line.replace("IN_STREAM, OUT_STREAM", 'IN_STREAM')
    #        line = line.replace("MODULE_NAME", func_name)
    #        line = line.replace("IN_STREAM", in_streams).replace("OUT_STREAM", out_streams)
    #        line = line.replace("NUM_OUT", str(len(comps[c]['out'])))
    #        f.write(line + '\n')
            
    ## For the "new_stream = func(input_stream, output_stream) set up
    ## Not used in the "output_stream = func(input_stream)" set up
    ## Create a PStreams Stream object from the names of each stream/edge in the graph
    #for op in out_ports:
    #    instance = op["process"].encode('ascii','ignore')[x:]
    #    port = op["port"].encode('ascii','ignore')
    #    stream_name = instance + '_' + port
    #    f.write( stream_name + ' = Stream(\''+ stream_name + '\')\n')
    
    ## Create a PStreams Stream object from outputs of modules with no input (source module)
    #for c in comps:
    #    if len(comps[c]['in']) == 0:
    #        for op in out_ports:
    #            if op['process'].encode('ascii','ignore')[:-6] == c:
    #                instance = op["process"].encode('ascii','ignore')[x:]
    #                port = op["port"].encode('ascii','ignore')
    #                stream_name = instance + '_' + port
    #                f.write( stream_name + ' = Stream(\''+ stream_name + '\')\n')
    
    ## Call modules with names of their input and output ports
    #for c in comps:
    #    func_name = c.encode('ascii','ignore')[x:]
    #    in_streams = ''
    #    for ip in comps[c]['in']:
    #        in_streams = '\'' + ip.encode('ascii','ignore') + '\', ' + in_streams
    #    
    #    out_streams = ''
    #    for op in comps[c]['out']:
    #        out_streams = '\'' + op.encode('ascii','ignore') + '\', ' + out_streams
    #
        #f.write(func_name + '_in_stream([' + in_streams + '],[' + out_streams + '])\n')
    #    f.write(func_name + '([' + in_streams[:-2] + '],[' + out_streams[:-2] + '])\n')
        
    ## Make connections by calling modules with input and output streams
    instances = data["processes"].keys()
    #pprint(instances)
    
    #for i in instances:
    #    func_name = i.encode('ascii','ignore')[x:-6]
    #    in_streams = ''
    #    out_streams = ''
    #    for conn in data['connections']:
    #        sp = conn['src']['process'].encode('ascii','ignore')
    #        if sp == i:
    #            out_streams = sp[x:] + '_' + conn['src']['port'].encode('ascii','ignore')+ ', ' +  out_streams 
    #            
    #        tp = conn['tgt']['process'].encode('ascii','ignore')
    #        if tp == i:
    #            in_streams = tp[x:] + '_' + conn['tgt']['port'].encode('ascii','ignore')+ ', ' +  in_streams
                
                
    #    f.write(func_name + '_in_stream([' + in_streams[:-2] + '],[' + out_streams[:-2] + '])\n')
    

    ## Create dict of each module instance with it's in and out streams

    
    ## Write instance dict contents to file as a function call
    #for i in instance_dict:
    #    in_streams = ''
    #    out_streams = ''
    #    for each in instance_dict[i]['in']:
    #        in_streams = each[x:] + ', ' + in_streams
    #    for each in instance_dict[i]['out']:
    #        out_streams = each[x:] + ', ' + out_streams
    #    
    #    f.write(i[x:-6] + '_in_stream([' + in_streams[:-2] + '],[' + out_streams[:-2] + '])\n')
        
    
    instance_dict = make_instance_dict(data, instances)
    #pprint(instance_dict)
    instance_dict_copy, output_str = function_calls(instance_dict)
    f.write(output_str)
    
    #execfile(output_file_name)
    
    return output_file_name

# from Animation.py
'''
# Returns the 2 strings whose values are the edge and node arrays for the JS
# file
def make_graph(agent_descriptor_dict, stream_names_tuple):
    nodes = 'nodes: [\n'
    edges = 'edges: [\n'
    
    # Construct nodes string
    for name in agent_descriptor_dict.keys():
        node_line = '\t{ data: { id: \''+ name + '\', name:\'' + name +\
                        ' ''\'} },\n'
        nodes = nodes + node_line
    
    print('--------stream names tuple-------------')
    pprint(stream_names_tuple)
    # Construct edges string
    for s in stream_names_tuple:
        # src_name is the name of the component that the stream s is from
        src_name = s.split('_PORT_')[0]
        # tgt_name is found from the list of input streams of the components
        tgt_name = str()
        for i in agent_descriptor_dict.keys():
            if s in agent_descriptor_dict[i][0]:
                tgt_name = i
                break
            
        edge_line = '\t{ data: { stream: \'' + s + '\', source: \'' + src_name + '\', target: \'' +\
                    tgt_name +'\', name:\'' + s + ':' + '\'} },\n'
        edges = edges + edge_line
        
            
    nodes = nodes[:-2] + ']'
    edges = edges[:-2] + ']'
    return nodes, edges
'''

#from MakeNetwork.py

'''
## Generate my special JSON file
def make_my_JSON(instance_dict, comp_list):

    stream_names_tuple = make_stream_names_tuple(instance_dict, comp_list)
    agent_descriptor_dict = make_agent_descriptor_dict(instance_dict, comp_list)
    
    output_file_name = 'agent_descriptor.json'
    f = open(output_file_name, 'w')
    f.write('{\n')
    f.write('\"agent_descriptor_dict\":\n')
    f.write(agent_descriptor_dict)
    f.write(',\n')
    f.write('\"stream_names_tuple\":\n')
    f.write(stream_names_tuple)
    f.write('\n}')
    f.close()
    return output_file_name
'''

'''
# STEP 1
# PROVIDE CODE OR IMPORT PURE (NON-STREAM) FUNCTIONS

from random import randint
def rand(f_args):
    max_integer = f_args[0]
    return randint(0, max_integer)

#def split(m, f_args):
#    divisor = f_args[0]
#    return [_no_value, m] if m%divisor else [m, _no_value]

#def print_value(v, index):
#        #print name + '[' , index , '] = ', v
#        print '[' , index , '] = ', v
#        return (index+1)
'''

'''
# STEP 2
# SPECIFY THE NETWORK.
def make_js_seq(instance_dict, json_file_name):
   
    # Specify names of all the streams.
    #stream_names_tuple = ('random_stream', 'multiples_stream', 'non_multiples_stream')
    #stream_names_tuple = ('generate_stream_of_random_integers_PORT_output', 'split_stream_PORT_multiples', 'split_stream_PORT_nonmultiples')
    
    # Specify the agents:
    # key: agent name
    # value: list of input streams, list of output streams, function, function type,
    #        tuple of arguments, states
    #
    #agent_descriptor_dict = make_agent_descriptor_dict(instance_dict, comp_list)

   
    #agent_descriptor_dict = {
    #    'generate_stream_of_random_integers': [
    #        [], ['generate_stream_of_random_integers_PORT_output'], generate_of_random_integers, 'element', (100,), None],
    #    'split_stream': [
    #        ['generate_stream_of_random_integers_PORT_output'], ['split_stream_PORT_multiples', 'split_stream_PORT_nonmultiples'],
    #        split, 'element', (2,), None],
    #    'print_value_stream': [
    #        ['generate_stream_of_random_integers_PORT_output'], [], print_value, 'element', None, 0],
    #    'print_value_stream1': [['split_stream_PORT_multiples'], [], print_value, 'element', None, 0],
    #    'print_value_stream2': [['split_stream_PORT_nonmultiples'], [], print_value, 'element', None, 0]
    #}
    
    
    
    comp_list = make_comp_list(instance_dict)
    my_json_file_name = make_my_JSON(instance_dict, comp_list)
    
    ## Make agent_descriptor_dict, stream_names_tuple
    agent_descriptor_dict, stream_names_tuple = JSON_to_descriptor_dict_and_stream_names(my_json_file_name)
    #agent_descriptor_dict = test(instance_dict, comp_list)
    #stream_names_tuple = make_stream_names_tuple(instance_dict, comp_list)
        
    
    print('---------agent_descriptor_dict-------')
    pprint(agent_descriptor_dict)
    print('---------stream_names_tuple-------')
    pprint(stream_names_tuple)
    
    # STEP 3: MAKE THE NETWORK
    stream_dict, agent_dict, t_dict = make_network(
        stream_names_tuple, agent_descriptor_dict)
    print('------stream_dict_-------')
    pprint(stream_dict)
    ## # Only for debugging
    ## for key, value in s_dict.items():
    ##     print 'stream name', key
    ##     print 'stream', value

    ## for key, value in a_dict.items():
    ##     print 'agent name', key
    ##     print 'agent', value

    ## for key, value in t_dict.items():
    ##     print 'timer name is', key
    ##     print 'timer', value

    # STEP 4: DRIVE THE NETWORK BY APPENDING
    #      VALUES TO TIMER STREAMS
    
    ## AND ALSO MAKE STRINGS TO BE WRITTEN TO OUTPUT FILE
    
    
    # val_str is a list of values of each time step,
    # concatnated in one long, comma separated string
    val_str = str()
    
    # list of the streams in order
    streams_list = []
    streams_list_done = False
    
    # Doesn't work for copies of streams:
    #    it gives 3 names, even when 1 was called twice
    # Create a list of stream names for the JS file
    #for stream_name in stream_names_tuple:
        # Create list of all streams at each time step
        #streams_list.append(stream_name)
    #print '-----------streams_list-------------'
    #pprint(streams_list)
    
    for t in range(5):
        print '--------- time step: ', t
        # Append t to each of the timer streams
        for stream in t_dict.values():
            print '-------', stream.name
            stream.append(t)
            ## for stream in stream_dict.values():
            ##     stream.print_recent()

            # Print messages in transit to the input port
            # of each agent.
            for agent_name, agent in agent_dict.iteritems():
                descriptor = agent_descriptor_dict[agent_name]
                input_stream_list = descriptor[0]
                for stream_name in input_stream_list:
                    print '--------input_stream_list: ', input_stream_list
                    # Create list of all streams at each time step
                    if streams_list_done == False:
                        streams_list.append(stream_name)
                    
                    # Get the correct stream object
                    stream = stream_dict[stream_name]
                    
                    # value is a string of this form:
                    # [4]
                    value = str(stream.recent[stream.start[agent]:stream.stop])
                    #print '----value------'
                    #print value[1:-1]
                    val_str = val_str + '\'' + value[1:-1] + '\' ,'
                    #val_str = val_str + index_and_value.split(' = ')[1] + ','
                    
                    print "messages in ", stream_name, "to", agent.name
                    print stream.recent[stream.start[agent]:stream.stop]
            streams_list_done = True

    val_str = 'var value = [' + val_str[:-1] + '];'
    
    # stream_str is a list of all streams, 
    # selector_str is the list of streams, but formatted 
    # to be used as selectors in JS
    stream_str = str()
    selector_str = str()
    for s in streams_list:
        selector_str = selector_str + '\'edge[stream= "' + s + '"]\', '
        stream_str = stream_str + '\'' + s + '\', '
    selector_str = 'var edge = [' + selector_str[:-1] + '];'
    stream_str = 'var stream_names = [' + stream_str[:-1] + '];'
    
    
    pprint(stream_str + '\n' +  selector_str + '\n' + val_str)
    return stream_str + '\n' +  selector_str + '\n' + val_str
## t_dict['generate_random'].append(0)
## s_dict['random_stream'].print_recent()
## s_dict['multiples_stream'].print_recent()
## s_dict['non_multiples_stream'].print_recent()

## t_dict['split'].append(1)
## s_dict['random_stream'].print_recent()
## s_dict['multiples_stream'].print_recent()
## s_dict['non_multiples_stream'].print_recent()

if __name__ == '__main__':
    main()
'''

import json
from pprint import pprint
from graph_to_program1 import *
from example import *
from MakeNetwork import *

import webbrowser
import os
#from root.nested import MakeNetwork


def make_js(conn, instance_dict, x):
    ## Open new file to write to
    output_file_name = 'try_cytoscape/graph.js'
    f = open(output_file_name, 'w')
    template_file_name = 'try_cytoscape/code.js'
    t = open(template_file_name, 'r')
    
    ## Make comp_list, a dictionary of each component type and its ids
    comp_list = make_comp_list(instance_dict, x)
    #pprint('this is makejs complist\n:')
    #pprint(comp_list)
    
    ## Make conn_dict, dict of instance name and the instances
    ## it outputs to
    #print('this is conn\n')
    #pprint(conn)
    conn_dict = make_conn_dict(conn, x)
    #print('conn_dict is: \n')
    #pprint(conn_dict)
    
    ## Working here
    nodes = 'nodes: [\n'
    edges = 'edges: [\n'
    
    for i in comp_list.keys():
        for id in comp_list[i]:
            name = name_with_new_id(comp_list, i, id)
        
            node_line = '\t{ data: { id: \''+ name + '\', name:\'' + name +\
                            ' ''\'} },\n'
            nodes = nodes + node_line

    for i in conn_dict.keys():
        #pprint('i is:\n')
        #pprint(i)
        for tgt in conn_dict[i]:
            #t_arr = tgt.split('_')
            #tgt = name_with_new_id(comp_list, str(tgt), t_arr[len(t_arr)-1])
            tgt_name, tgt_id = clean_id(tgt)
            tgt_name = name_with_new_id(comp_list, tgt_name, tgt_id)
            #s_arr = i.split('_')
            #src = name_with_new_id(comp_list, str(i), s_arr[len(s_arr)-1]) ##TO DO!! get id
            src_name, src_id = clean_id(i)
            src_name = name_with_new_id(comp_list, src_name, src_id)
            
            edge_line = '\t{ data: { source: \'' + src_name + '\', target: \'' +\
                        tgt_name +'\', name:\'' + 'stream_name: ' + 'value' + '\'} },\n'
            edges = edges + edge_line
            
            
    nodes = nodes[:-2] + ']'
    edges = edges[:-2] + ']'
    
    #f.write(nodes + ',\n' + edges)
    for line in t:
        line = line.replace('HERE', nodes + ',\n' + edges)
        f.write(line)
    
    new = 2    
    url = "try_cytoscape/main.html"
    webbrowser.open(url,new=new)

## Generates an animated graph for Cytoscape.js
def make_js_animate(conn, instance_dict, x):
    
    ## Make comp_list, a dictionary of each component type and its ids
    comp_list = make_comp_list(instance_dict, x)
    #pprint('this is makejs complist\n:')
    #pprint(comp_list)
    
    ## Make conn_dict, dict of instance name and the instances
    ## it outputs to
    #print('this is conn:')
    #pprint(conn)
    conn_dict = make_conn_dict(conn, x)
    #print('conn_dict is: \n')
    #pprint(conn_dict)
    
    ## Working here
    nodes = 'nodes: [\n'
    edges = 'edges: [\n'
    
    for i in comp_list.keys():
        for id in comp_list[i]:
            name = name_with_new_id(comp_list, i, id)
        
            node_line = '\t{ data: { id: \''+ name + '\', name:\'' + name +\
                            ' ''\'} },\n'
            nodes = nodes + node_line

    for i in conn_dict.keys():
        #pprint('i is:\n')
        #pprint(i)
        for s in conn_dict[i]:
            #Replace random id with 0, 1, 2...
            tgt_name, tgt_id = clean_id(s['tgt'])
            tgt_name = name_with_new_id(comp_list, tgt_name, tgt_id)
            
            #Replace random id with 0, 1, 2...
            src_name, src_id = clean_id(i)
            src_name = name_with_new_id(comp_list, src_name, src_id)
            
            #Get stream name: component_PORT_portname
            # 'x'* x is a placeholder because the rename() assumes that 
            # arg is in form: projname/compname_id_port
            #print('-----------port-----------')
            #pprint(s)
            stream_name = rename_stream(['x'* x + i + '_' + s['port']], comp_list, x)[0]
            
            edge_line = '\t{ data: { stream: \'' + stream_name + '\', source: \'' + src_name + '\', target: \'' +\
                        tgt_name +'\', name:\'' + stream_name + ':' + '\'} },\n'
            edges = edges + edge_line
            
            
    nodes = nodes[:-2] + ']'
    edges = edges[:-2] + ']'
    
    return nodes, edges
 
# Make .js arrays that determine the order of animation
# by generating a string
# from the output file of values
def make_animation_seq(stream_vals):
    ## Open computed streams file to read from
    stream_vals = 'stream_vals'
    output_file_name = stream_vals + '.csv'
    f = open(output_file_name, 'r')
    
    # all_js_arr is the JS text string that we generate
    # it's an array of vals for each unique stream
    all_js_arr = str()
    # seen_streams keep track of unique streams so that we don't have
    # duplicates
    seen_streams = []
    
    print('----curr line -----')
    curr_line = f.readline()
    print curr_line
    
    print('----curr stream and val ----')
    curr_stream = curr_line.strip().split('[')[0]
    val = curr_line.strip().split('= ' )[1]
    prev_index = int(curr_line.split('[')[1].split(']')[0])
    
    all_js_arr = 'var seq = {\n' + str(curr_stream) + ': [' + val
    seen_streams = [curr_stream]
    print(all_js_arr)
    print(curr_stream, val)
    print ('----end curr stream and val-----')
    
    
    for line in f:
        
        pprint('-------line---------')
        pprint(line)
        
        print('--------this stream and val -----')
        this_stream = line.split('[')[0]
        this_index = int(line.split('[')[1].split(']')[0])
        this_val = line.strip().split('=')[1]
        print this_stream, this_val, this_index
        
        if this_stream == curr_stream and this_index > prev_index:
            all_js_arr = all_js_arr + this_val
            #print(curr_js_arr)
            
            prev_index = this_index
        elif this_stream not in seen_streams:
            print(this_stream + ' is not in')
            pprint(seen_streams)
            # end current array
            all_js_arr = all_js_arr[:-1] + '],\n'
            # add it to the full list of arrays
            #all_js_arr = all_js_arr + curr_js_arr
            
            # curr_stream is now the new stream name
            curr_stream = this_stream
            # store the name of the finished stream so we don't repeat it
            seen_streams.append(curr_stream)
            # starting a new JS array text line
            all_js_arr = all_js_arr + str(curr_stream) + ': [' + this_val
            #print '--------new line-----------'
            #print(all_js_arr)
            
            prev_index = this_index
          
        else:
            #print 'skip'
            #pprint(seen_streams)
            continue
    
    # clear file of values after done processing because the write_streams
    # component in 'components.py" doesn't know how to overwrite the file
    # after each run of the whole program
    f2 = open(output_file_name, 'w')
    f2.write('')
    
    print('------all js arr-------')
    all_js_arr = all_js_arr[:-1] + ']\n}'
    pprint(all_js_arr)
    
    return all_js_arr

## Reads a csv of the output values from pstreams_output and makes JS from it
def make_animate_seq2(stream_vals):
    ## Open computed streams file to read from
    #stream_vals = 'stream_vals_temp'
    output_file_name = stream_vals + '.csv'
    f = open(output_file_name, 'r')
    
    # all_js_arr is the JS text string that we generate
    # it's an array of vals for each unique stream
    all_js_arr = {}
    # seen_streams keep track of unique streams so that we don't have
    # duplicates
    seen_streams = []
    
    print('----curr line -----')
    curr_line = f.readline()
    print curr_line
    
    print('----curr stream and val ----')
    curr_stream = curr_line.strip().split('[')[0]
    val = curr_line.strip().split('= ' )[1]
    prev_index = int(curr_line.split('[')[1].split(']')[0])
    
    all_js_arr[curr_stream] = [val]
    seen_streams = [curr_stream]
    print(all_js_arr)
    print(curr_stream, val)
    print ('----end curr stream and val-----')
    
    
    for line in f:
        pprint('-------line---------')
        pprint(line)
        
        print('--------this stream and val -----')
        this_stream = line.split('[')[0]
        this_index = int(line.split('[')[1].split(']')[0])
        this_val = line.strip().split('=')[1]
        print this_stream, this_val, this_index
        
        if this_stream == curr_stream and this_index > prev_index:
            all_js_arr[this_stream].append(this_val)
            #print(curr_js_arr)
            
            prev_index = this_index
        elif this_stream not in seen_streams:
            print(this_stream + ' is not in')
            pprint(seen_streams)
                        
            # curr_stream is now the new stream name
            curr_stream = this_stream
            # store the name of the finished stream so we don't repeat it
            seen_streams.append(curr_stream)
            # starting a new JS array text line
            all_js_arr[str(curr_stream)] = [this_val]
            print '--------new line-----------'
            print(all_js_arr)
            
            prev_index = this_index
          
        else:
            print 'skip'
            pprint(seen_streams)
    

    
    print('------all js arr-------')
    pprint(all_js_arr)
    
    ## Make JS array, value, of the stream data in order
    value = str()
    for i in range(len(all_js_arr[all_js_arr.keys()[0]])):
        for s in all_js_arr.keys():
            value = value + '\'' + all_js_arr[s][i][:-1] + '\','
    vals = 'var value = [' + value[:-1] + '];'
    
    ## Make JS array, edge, of the edge filters for each stream
    ## Make JS array, stream_names, of the names of each stream
    edges = str()
    stream_names = str()
    for s in all_js_arr.keys():
        edges = edges + '\'edge[stream= "' + s + '"]\', '
        stream_names = stream_names + '\'' + s + '\', '
    edges = 'var edge = [' + edges[:-1] + '];'
    stream_names = 'var stream_names = [' + stream_names[:-1] + '];'
    
    
    
    # clear file of values after done processing because the write_streams
    # component in 'components.py" doesn't know how to overwrite the file
    # after each run of the whole program
    f2 = open(output_file_name, 'w')
    f2.write('')
    
    return edges + '\n' + vals + '\n' + stream_names
    

def make_animate_code(conn, instance_dict, x, json_file_name):
    ## Open new file to write to
    output_file_name = 'try_cytoscape/animate_graph.js'
    f = open(output_file_name, 'w')
    # Open template file to copy from and fill out
    template_file_name = 'try_cytoscape/animate_code.js'
    t = open(template_file_name, 'r')
    
    nodes, edges = make_js_animate(conn, instance_dict, x)
    #seq = make_animate_seq2(stream_vals)
    seq = make_js_seq(instance_dict, json_file_name, x)
    for line in t:
        line = line.replace('ELEMENTS', nodes + ',\n' + edges)
        line = line.replace('SEQUENCE', seq)
        f.write(line)
        
    
    new = 2    
    url = "try_cytoscape/main.html"
    webbrowser.open(url,new=new)
    
    
def animate(json_file_name):
    with open(json_file_name) as data_file:
        data = json.load(data_file)
        instances = data["processes"].keys()
        instance_dict_copy = make_instance_dict(data, instances)
        x = len(instances[0].encode('ascii','ignore').split('/')[0]) + 1
        conn = data['connections']
        
        make_animate_code(conn, instance_dict_copy, x, json_file_name)
        #make_js_animate(data['connections'], instance_dict_copy, x)
        #make_animation_seq('stream_vals')
        #make_animate_seq2('stream_vals')

'''
## Combine animate() and make_animate_code so that I don't have to pass
## the variable flowhub as argument
def animate(json_file_name):
    flowhub = True
    with open(json_file_name) as data_file:    
        data = json.load(data_file)
        if 'agent_descriptor_dict' in data.keys():
            flowhub = False
            
        instances = data["processes"].keys()
        instance_dict = make_instance_dict(data, instances)
        x = len(instances[0].encode('ascii','ignore').split('/')[0]) + 1
        conn = data['connections']
        
    ## Open new file to write to
    output_file_name = 'try_cytoscape/animate_graph.js'
    f = open(output_file_name, 'w')
    # Open template file to copy from and fill out
    template_file_name = 'try_cytoscape/animate_code.js'
    t = open(template_file_name, 'r')
    
    nodes, edges = make_js_animate(conn, instance_dict, x)
    #seq = make_animate_seq2(stream_vals)
    seq = make_js_seq(instance_dict, flowhub, x)
    for line in t:
        line = line.replace('ELEMENTS', nodes + ',\n' + edges)
        line = line.replace('SEQUENCE', seq)
        f.write(line)
        
    
    new = 2    
    url = "try_cytoscape/main.html"
    webbrowser.open(url,new=new)
'''


## Generate js file for Arbor.js
def make_js_arbor(conn, instance_dict, x):
    comp_list = make_comp_list(instance_dict, x)
    #pprint('this is makejs complist\n:')
    #pprint(comp_list)
    
    ## Open new file to write to
    output_file_name = 'arbor/docs/sample-project/graph.js'
    f = open(output_file_name, 'w')
    
    all = 'var myvar = { \n\t edges:{\n'
    #pprint(conn)
    conn_dict = {}
    for i in conn:
        if 'src' in i.keys():
            name = str(i['src']['process'])[x:]
            conn_dict[name] = []
        
    for i in conn:
        if 'src' in i.keys():
            #src_name, src_id = clean_id(str(i['src']['process']))
            #tgt_name, tgt_id = clean_id(str(i['tgt']['process']))
            src_name = str(i['src']['process'])[x:]
            tgt_name = str(i['tgt']['process'])[x:]
            conn_dict[src_name].append(tgt_name)
    #print('conn_dict is: \n')
    #pprint(conn_dict)
    ## Working here    
    for i in conn_dict.keys():
    
        comp = '\t\t' + str(i) +': {\n'
        #for o in i[2]:
        #    params = ": {value: '0'}"
        #    comp = comp + '\t{' + o + params + '}, \n'
        #comp = comp[:-4] + '}, \n'
        params = ":{data:{name: '0'}}"
        for tgt in conn_dict[i]:
            comp = comp + '\t\t\t'+ tgt + params + ',\n'
        #comp = comp + '\t\t\t'+ str(i['tgt']['process'][x:]) + params + '}, \n'
        all = all + comp[:-2] + '},\n'
    all = all[:-3] + '}}}'
    f.write(all)

## Generate JS for Cytoscape.js. Makes a static graph.

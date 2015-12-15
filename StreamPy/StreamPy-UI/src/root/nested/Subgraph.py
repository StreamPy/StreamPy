'''
This module handles unwrapping nested subgraphs,
provided the JSON files of each graph.

'''
import json
from pprint import pprint
import webbrowser
import os
import re
from array import array
from copy import deepcopy

from MakeNetwork import *
from Animation import *
from Stream import Stream, _no_value, _multivalue
from Agent import Agent
from OperatorsTestParallel import stream_agent

from components import *
from helper import *


def make_json(json_file_name):
    '''
    Checks and converts input JSON file to a JSON file
    in my special format if it's not already

    Parameters
    ----------
    json_file_name : str
        Path to JSON file to be converted

    Returns
    -------
    my_json_file_name : str
        Path to converted JSON file

    '''
    # Import JSON file as JSON object
    with open(json_file_name) as data_file:
        json_data = json.load(data_file)

    # Check if the input JSON is from Flowhub or already in my format
    if 'agent_descriptor_dict' not in json_data.keys():

        # Make helper data structures from Flowhub JSON
        instances = json_data["processes"].keys()
        instance_dict = make_instance_dict(json_data, instances)
        comp_list = make_comp_list(instance_dict)

        # Make a JSON file in the format I want from Flowhub's JSON
        my_json_file_name = make_my_JSON(instance_dict, comp_list, json_data)

    else:
        # The input JSON is already in the format I want
        my_json_file_name = json_file_name

    return my_json_file_name


def unwrap_subgraph(my_json_file_name):
    '''
    Recursively exposes nested subgraphs to be executed for the animation.

    Parameters
    ----------
    my_json_file_name : str
        Path to JSON file of my special format to be converted

    Returns
    -------
    "json_file.json" : str
        json_file.json is the name of the file with the
        fully exposed graph

    '''

    # Go through all functions/modules in json file and make sure they're in
    # components_test.py. Otherwise, there might be a subgraph.

    with open(my_json_file_name) as json_file_original:
        j = json.load(json_file_original)

    # Make array of functions in components.py
    # (also includes elements like '__builtins__', '__doc__', '__file__')
    comps_funcs = dir(components)

    # Make array of functions/components in JSON
    JSON_funcs = []
    for i in j['agent_descriptor_dict'].keys():
        JSON_funcs.append(j['agent_descriptor_dict'][i][2])

    # If there are functions in the graph not in components.py...
    # they are most likely subgraphs, so collect them in 'unfound_comps'
    unfound_comps = []
    for f in JSON_funcs:
        if f not in comps_funcs:
            unfound_comps.append(f)

    # Initialize new dictionary with values of the original graph.
    new_dict = {}
    new_dict['agent_descriptor_dict'] = deepcopy(j['agent_descriptor_dict'])
    new_dict['stream_names_tuple'] = deepcopy(j['stream_names_tuple'])

    # If there are potential subgrahps...
    if len(unfound_comps) > 0:
        for unfound in unfound_comps:
            try:
                # Look for a corresponding JSON for corresponding subgraph
                # TODO: get path from run.py
                # path = '/home/klyap/Downloads/'
                path = '/Users/kerleeyap/Downloads/'
                # path = 'JSON/'
                new_json = unfound + '.json'

                # Grab the exposed in and out ports from original JSON:
                with open(path + new_json) as new_json_file:
                    subgraph_json = json.load(new_json_file)

                new_json = make_json(path + new_json)

                with open(new_json) as new_json_file:
                    subgraph_dict = json.load(new_json_file)
                
                print 'before anything:'
                pprint(subgraph_dict['stream_names_tuple'])
                # Pop agent_desc_dict entry of the current unfound component
                # as 'unfound_entry'
                unfound_entry = \
                    deepcopy(new_dict['agent_descriptor_dict'][unfound])
                del new_dict['agent_descriptor_dict'][unfound]

                # Check for a component in newly unwrapped comps
                # that was used outside it and
                # rename accordingly.
                for comp in subgraph_dict['agent_descriptor_dict'].keys():
                    # Check if this component has multiple instances
                    occurences = 0
                    outside_comps = new_dict['agent_descriptor_dict'].keys()
                    for outside_comp in outside_comps:
                        clean_comp = comp
                        my_id = int()
                        m = re.search(r'\d+$', clean_comp)
                        if m is not None:
                            clean_comp = clean_comp.replace(m.group(), '')
                            my_id = int(m.group())

                        clean_outside_comp = outside_comp
                        m = re.search(r'\d+$', clean_outside_comp)
                        if m is not None:
                            clean_outside_comp = clean_outside_comp.\
                                replace(m.group(), '')

                        if clean_comp == clean_outside_comp:
                                occurences += 1

                    # If there are multiple instances...
                    if occurences > 0:
                        # Rename the component in agent_desc_dict appropriately
                        clean_comp = comp.strip(str(my_id)) + \
                                     str(my_id + occurences)
                        subgraph_dict['agent_descriptor_dict'][clean_comp] = \
                            subgraph_dict['agent_descriptor_dict'][comp]
                        del subgraph_dict['agent_descriptor_dict'][comp]

                        # Rename contents of this entry in agent_desc_dict
                        # (ie. input and output streams)
                        for c in subgraph_dict['agent_descriptor_dict']:
                            # Rename input streams
                            subgraph_inputs = \
                                subgraph_dict['agent_descriptor_dict'][c][0]
                            for s in subgraph_inputs:
                                if s.split("_PORT_")[0] == comp:
                                    new_s = clean_comp + '_PORT_' + \
                                            s.split('_PORT_')[1]
                                    subgraph_inputs.append(new_s)
                                    subgraph_inputs.remove(s)
                            # Rename output streams
                            subgraph_outputs = \
                                subgraph_dict['agent_descriptor_dict'][c][1]
                            for s in subgraph_outputs:
                                if s.split("_PORT_")[0] == comp:
                                    new_s = clean_comp + \
                                            '_PORT_' + \
                                            s.split('_PORT_')[1]
                                    subgraph_outputs.append(new_s)
                                    subgraph_outputs.remove(s)

                        # Rename appropriately in these dicts and tuple:
                        # inports, outports and stream_names_tuple
                        for port in subgraph_dict['inports']:
                            element = subgraph_dict['inports'][port]
                            if element.split('_PORT_')[0] == comp:
                                subgraph_dict['inports'][port] = \
                                    clean_comp + \
                                    '_PORT_' + \
                                    element.split('_PORT_')[1]

                        for port in subgraph_dict['outports']:
                            element = subgraph_dict['outports'][port]
                            if element.split('_PORT_')[0] == comp:
                                subgraph_dict['outports'][port] = \
                                    clean_comp + \
                                    '_PORT_' + \
                                    element.split('_PORT_')[1]
                                    
                        for c in subgraph_dict['stream_names_tuple']:
                            if c.split('_PORT_')[0] == comp:
                                subgraph_dict['stream_names_tuple'].\
                                    append(clean_comp +
                                           '_PORT_' +
                                           c.split('_PORT_')[1])
                                subgraph_dict['stream_names_tuple'].remove(c)
                        
                        print 'after renaming stream names tuple:'
                        pprint(subgraph_dict['stream_names_tuple'])
                        
                # Insert new, renamed unwrapped components into 'new_dict'
                for comp in subgraph_dict['agent_descriptor_dict'].keys():
                    new_dict['agent_descriptor_dict'][comp] = \
                        subgraph_dict['agent_descriptor_dict'][comp]

                # Get exposed out streams and in streams of subgraph
                inports = subgraph_dict['inports']
                outports = subgraph_dict['outports']

                # FOR IN PORTS:
                for comp in new_dict['agent_descriptor_dict']:
                    new_inputs = []
                    for s in new_dict['agent_descriptor_dict'][comp][0]:
                        # If exposed output streams come from a comp in
                        # this subgraph, add this to that comp's input streams
                        renamed_stream = s
                        if unfound in s:
                            renamed_stream = outports[s.split('_PORT_')[1]]
                        new_inputs.append(renamed_stream)
                    new_dict['agent_descriptor_dict'][comp][0] = new_inputs

                # Now check components outside subgraphs for those
                # that connect to the inputs in our list
                # These streams in 'new_inputs' are currently named after
                # the in port.
                # We want it to be the out port of the prev component.
                for i in range(len(inports.values())):
                    # Get component name from inport stream
                    # ie. compname_PORT_in
                    comp_name = inports.values()[i].split('_PORT_')[0]

                    # Match it with a input stream of the same index
                    new_dict['agent_descriptor_dict'][comp_name][0].\
                        append(unfound_entry[0][i])

                # FOR OUT PORTS:
                for o in outports.values():
                    # Assign o to comp_name in agent_desc_dict
                    comp_name = o.split('_PORT_')[0]
                    new_dict['agent_descriptor_dict'][comp_name][1].append(o)
                
                # FOR 'STREAM_NAMES_TUPLE':
                print 'about to add this into new dict'
                pprint(subgraph_dict['stream_names_tuple'])
                # Add in internal/hidden streams
                for s in subgraph_dict['stream_names_tuple']:
                    new_dict['stream_names_tuple'].append(s)

                # Add in inport streams
                for s in subgraph_dict['inports'].values():
                    if s not in new_dict['stream_names_tuple']:
                        new_dict['stream_names_tuple'].append(s)

                # Add in outport streams
                for s in subgraph_dict['outports'].values():
                    if s not in new_dict['stream_names_tuple']:
                        new_dict['stream_names_tuple'].append(s)

                # Remove wrongly named streams
                # (ie. subgraph_PORT_stream -> component_PORT_stream)
                for s in new_dict['stream_names_tuple']:
                    if unfound in s:
                        temp_dict = deepcopy(new_dict['stream_names_tuple'])
                        temp_dict.remove(s)
                        new_dict['stream_names_tuple'] = temp_dict

            except NameError:
                print 'No such function or subgraph JSON file: ' + f
                return 'No such function or subgraph JSON file: ' + f

        # Recurse
        json_file = open('json_file.json', 'w')
        json.dump(new_dict, json_file)
        json_file.close()
        print '-----SUBGRAPH----'
        pprint(subgraph_dict)
        print '-----DICT--------'
        pprint(new_dict)
        return unwrap_subgraph('json_file.json')
    else:
        # All functions found and unwrapped!
        json_file = open('json_file.json', 'w')
        json.dump(new_dict, json_file)
        json_file.close()
        return 'json_file.json'

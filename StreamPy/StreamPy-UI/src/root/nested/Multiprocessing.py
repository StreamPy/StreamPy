from copy import deepcopy
from pprint import pprint

from MakeParallelNetworkParallel import *
# UNCOMMENT FOR PARALLELLLL and get back MakeParallelNet2
# from MakeParallelNetwork import *


# Make data structure for parallel processing
# Key: name of group
# Value: {agent_desc dict, input_stream_names_tuple, output_stream_names_tuple,
#          all_stream_names_tuple}
def parallel_dict(json_data):
    # Get the mini JSON files for each group
    # with agent_desc_dict and stream_names_tuple
    big_dict = {}
    for group_name in json_data['groups'].keys():
        #print '====' + group_name + '======='
        big_dict[group_name] = {}

        # Fill out these:
        big_dict[group_name]['agent_descriptor_dict'] = {}
        big_dict[group_name]['input_stream_names_tuple'] = []
        big_dict[group_name]['output_stream_names_dict'] = {}

        for node in json_data['groups'][group_name]:
            #print '-----' + node + '-----'
            for process in json_data['agent_descriptor_dict'].keys():
                if node == process:
                    # Add agent_desc to group
                    big_dict[group_name]['agent_descriptor_dict'][process]=\
                    json_data['agent_descriptor_dict'][process]

                    # Grab input streams
                    big_dict[group_name]['input_stream_names_tuple'] +=\
                    json_data['agent_descriptor_dict'][process][0]

                    # Grab output streams and put in dict as keys
                    # with empty str as value
                    for i in json_data['agent_descriptor_dict'][process][1]:
                        big_dict[group_name]['output_stream_names_dict'][i] =\
                        str()

                    # Remove this node from original
                    json_data = deepcopy(json_data)
                    del json_data['agent_descriptor_dict'][process]

        # Start with all input streams
        big_dict[group_name]['all_stream_names_tuple'] =\
         list(big_dict[group_name]['input_stream_names_tuple'])

        # Add each output stream that isn't an input stream
        for i in big_dict[group_name]['output_stream_names_dict'].keys():
            if i not in big_dict[group_name]['all_stream_names_tuple']:
                big_dict[group_name]['all_stream_names_tuple'].append(i)



    ## Process leftover components (not in group), unwrap
    ## and add to big_dict as a group called "main"
    #pprint(json_data)

    # Fill out group called 'leftover':
    # Add agent_desc to group 'leftover'
    big_dict['leftover'] = {}
    big_dict['leftover']['agent_descriptor_dict']=\
    json_data['agent_descriptor_dict']
    big_dict['leftover']['input_stream_names_tuple'] = []
    big_dict['leftover']['output_stream_names_dict'] = {}


    for process in json_data['agent_descriptor_dict']:
        # Grab input streams
        big_dict['leftover']['input_stream_names_tuple'] +=\
        json_data['agent_descriptor_dict'][process][0]

        # Grab output streams and put in dict as keys
        # with empty str as value
        print '=====agent_descriptor_dict'
        pprint(json_data['agent_descriptor_dict'])
        for i in json_data['agent_descriptor_dict'][process][1]:
            print '----', json_data['agent_descriptor_dict'][process][1]
            big_dict['leftover']['output_stream_names_dict'][i] =\
            str()
            pprint(big_dict['leftover']['output_stream_names_dict'])
        # Remove it from original
        json_data = deepcopy(json_data)
        del json_data['agent_descriptor_dict'][process]

    # Make 'all_stream_names_tuple'
    # Start with all input streams
    big_dict['leftover']['all_stream_names_tuple'] =\
     list(big_dict[group_name]['input_stream_names_tuple'])

    # Add each output stream that isn't an input stream
    for i in big_dict['leftover']['output_stream_names_dict'].keys():
        if i not in big_dict['leftover']['all_stream_names_tuple']:
            big_dict['leftover']['all_stream_names_tuple'].append(i)


    ## Now that all groups are made:
    ## go through each and distinguish exposed input & output streams

    for group_name in big_dict.keys():
        ## -----------Unwrap subgraphs----------------
        #big_dict = unwrap(big_dict)
        ## -------------------------------------------

        ## Identify exposed output streams for this group
        # If an output is an input to a component in this
        # group, then delete it
        A = big_dict[group_name]['input_stream_names_tuple']
        B = big_dict[group_name]['output_stream_names_dict'].keys()
        # C is the list of streams we want to delete from output streams
        C =\
        [x for x in B if x in A]

        # Delete each in C from output streams
        copy = deepcopy(big_dict[group_name]['output_stream_names_dict'])
        for i in C:
            del copy[i]
        big_dict[group_name]['output_stream_names_dict'] = copy

        ## Identify exposed input streams for this group
        # From all input streams,
        # delete the ones that come from a component
        # in this group
        A = big_dict[group_name]['agent_descriptor_dict'].keys()
        B = big_dict[group_name]['input_stream_names_tuple']
        C =\
        [x for x in B if x.split('_PORT_')[0] not in A]
        big_dict[group_name]['input_stream_names_tuple'] = C

    pprint(big_dict)

    output_stream_names_tuple_to_dict(big_dict)
    pprint(big_dict)

    return big_dict

## Replaces the output stream tup to dict with queue names
## Also adds last element to processes in agent_desc_dict,
## "call_streams"
def output_stream_names_tuple_to_dict(big_dict):
    counter = 1
    connecting_streams = []
    groups_left = big_dict.keys()

    # Start by looking for source groups
    for group in groups_left:
        # If a group has no exposed input stream:
        input_streams = big_dict[group]['input_stream_names_tuple']
        if input_streams == []:
            output_dict = {}
            # Make the corresponding dict with 'queue_1' as value
            for s_name in big_dict[group]['output_stream_names_dict']:
                big_dict[group]['output_stream_names_dict'][s_name] = 'queue_1'

            # Make a new key/value pair in big dict for this group
            big_dict[group]['queue'] = 'queue_1'

            # Keep track of this group
            for i in big_dict[group]['output_stream_names_dict'].keys():
                connecting_streams.append(i)
            print 'connecting_streams!: ', connecting_streams
            groups_left.remove(group)

            for group in big_dict:
                print 'group in big dict:'
                pprint(group)
                for comp in big_dict[group]['agent_descriptor_dict']:
                    if big_dict[group]['agent_descriptor_dict'][comp][0] == []:
                        big_dict[group]['agent_descriptor_dict'][comp].append(None)
                    else:
                        big_dict[group]['agent_descriptor_dict'][comp].append(None)

    # Iterate on the rest:
    while groups_left != []:
        print 'groups left:'
        pprint(groups_left)

        counter += 1
        print 'counter:' + str(counter)
        for group in groups_left:
            print 'group: ' + group

            input_streams = big_dict[group]['input_stream_names_tuple']
            print 'input_streams: ', input_streams
            print 'connecting_streams: ', connecting_streams
            for in_name in input_streams:
                if in_name in connecting_streams:
                    output_dict = {}
                    # Make the corresponding dict
                    for out_name in big_dict[group]['output_stream_names_dict'].keys():
                        big_dict[group]['output_stream_names_dict'][out_name] =\
                         'queue_' + str(counter)


                    # Keep track of this group
                    connecting_streams += big_dict[group]['output_stream_names_dict'].keys()
                    if group in groups_left:
                        groups_left.remove(group)

            # Mark this group with new key/val pair
            big_dict[group]['queue'] = 'queue_' + str(counter)

    return big_dict

# Take in a big dict of needed data structures to run parallel processing
# (aka execute "main" in MakeParallelNetwork.py)
def run_parallel(big_dict):
    # Create queue variables for each needed queue
    # (each group needs a new queue as input)
    queues = {}
    queue_count = 1
    for group in big_dict:
        queues['queue_' + str(queue_count)] = Queue()
        queue_count += 1
    print '-------queues---------'
    pprint(queues)

    # Create processes from big dict
    processes = {}
    process_count = 1
    for group in big_dict:
        processes['process_' + str(process_count)] =\
        Process(target= MakeParallelNetworkParallel.make_process,
                args= (queues[big_dict[group]['queue']],
                       big_dict[group]['all_stream_names_tuple'],
                       big_dict[group]['input_stream_names_tuple'],
                       big_dict[group]['output_stream_names_dict'],
                       big_dict[group]['agent_descriptor_dict'])
                       )
        process_count += 1
    print '---------all processes--------'
    pprint(processes)

    for p in processes:
        print '------process starting------'
        pprint(processes[p])
        processes[p].start()

    queues['queue_1'].put(('trigger', 0))


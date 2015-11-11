if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Stream import Stream
from Operators import stream_func
from instances import instance_dict
from components import *

def main():

    function_string = str()
    # Helper function to delete 'browser...'
    def delete_startswith_substring(s, substring):
        if s.startswith(substring):
            return s[len(substring):]
        else:
            return s

    # Make a copy of instance_dict and call it
    # instance_dict_copy.
    # instance_dict_copy remains unchanged throughout
    # this program, while instance_dict changes as
    # nodes are deleted from the graph.
    instance_dict_copy = dict()
    for component, connections in instance_dict.items():
        connections_copy = dict()
        connections_copy['in'] = connections['in']
        connections_copy['out'] = connections['out']
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
            if not connections['in']:
                sources.append(component)
        #print 'sources:', sources
        
        if not sources:
            print 'ERROR: GRAPH HAS CYCLES!'
            return


        for component_1 in sources:
            connections_1 = instance_dict[component_1]
            # outputs_1 is the list of outputs of component_1
            outputs_1 = connections_1['out']
            #print 'outputs_1', outputs_1

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
                        #print 'output_1 in inputs_2', component_2

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
        c[0] = delete_startswith_substring(c[0], 'trywrite/')
        c[1] = [delete_startswith_substring(v, 'trywrite/') for v in c[1]]
        c[2] = [delete_startswith_substring(v, 'trywrite/') for v in c[2]]

        # output_string is something like:
        # 'output_1, output_2, output_3 = ' if there is at least one
        # output, and is the empty string if there is no output.
        output_string = str()
        for o in c[2]:
            output_string = output_string + o + ', '
        # Delete the very last comma
        output_string = output_string[:-2]
        if output_string:
            output_string += ' = '
        #print 'output_string: ', output_string

        # input_string is '()' if there are no inputs.
        # and otherwise it is like: (input_1, input_2, input_3)
        if not c[1]:
            input_string = '()'
        else:
            input_string = str()
            input_string += '('
            for i in c[1]:
                input_string = input_string + i + ', '
            input_string = input_string[:-2]
            input_string += ')'
        #print 'input_string: ', input_string

        statement = output_string + c[0] + input_string
        print 'statement is: ', statement
        function_string += statement +  '\n'
        print
        print

    print 'function_string is:'
    print function_string
    
    return

if __name__ == '__main__':
    main()

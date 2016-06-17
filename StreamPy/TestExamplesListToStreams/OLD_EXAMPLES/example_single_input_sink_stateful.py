"""This module contains examples of the stateless single stream source
"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from ListOperators import stream_func

def print_next_and_mean_stream(input_stream):
    # List function: list, state -> state
    def print_next_and_mean_list(lst, state):
        number_of_values, sum_of_values = state
        for v in lst:
            number_of_values += 1
            sum_of_values += v
            print '{0}[{1}], value = {2}'.format(
                input_stream.name, number_of_values, v)
            print '{0}, number received = {1}, mean = {2:8.2f}'.format(
                input_stream.name, number_of_values,
                sum_of_values/float(number_of_values))
        state = (number_of_values, sum_of_values)
        return state

    return stream_func(
        list_func=print_next_and_mean_list,
        inputs=input_stream,
        num_outputs=0,
        state=(0, 0.0),
        call_streams=None)



def main():
    y_stream = Stream('y_stream')
    print_next_and_mean_stream(y_stream)
    y_stream.extend(range(10, 20, 2))
    y_stream.extend(range(40, 50, 2))
    
    

if __name__ == '__main__':
    main()

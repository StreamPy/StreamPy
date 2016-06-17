"""This module contains examples of the stateless single stream source
"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from ListOperators import stream_func

# Stream function
def averages_stream(input_stream):
    # List function: list, state -> list, state
    def averages_list(input_list, state):
        number_of_values, sum_of_values = state
        output_list = [0.0] * len(input_list)
        for i,v in enumerate(input_list):
            sum_of_values += v
            number_of_values += 1
            output_list[i] = sum_of_values/float(number_of_values)
        state = number_of_values, sum_of_values
        return (output_list, state)

    return stream_func(
        list_func=averages_list,
        inputs=input_stream,
        num_outputs=1,
        state=(0, 0.0),
        call_streams=None)




def main():
    def print_stream_recent(s):
        print s.name, " = ", s.recent[:s.stop]

    y_stream = Stream('y stream')
    z_stream = averages_stream(y_stream)
    z_stream.set_name('z')
    print_stream_recent(z_stream)

    y_stream.extend([3, 5])
    print_stream_recent(z_stream)

    y_stream.extend([1, 11])
    print_stream_recent(z_stream)

if __name__ == '__main__':
    main()

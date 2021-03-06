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
def cumulative_sum_of_streams(list_of_input_streams):
    # List function: list of lists, state -> list, state
    def cumulative_sum_of_lists(list_of_input_lists, cumulative):
        output_list = map(sum, zip(*list_of_input_lists))
        for i,v in enumerate(output_list):
            cumulative += output_list[i]
            output_list[i] = cumulative
        return (output_list, cumulative)

    return stream_func(
        list_func=cumulative_sum_of_lists,
        inputs=list_of_input_streams,
        num_outputs=1,
        state=0.0,
        call_streams=None)




def main():
    def print_stream_recent(s):
        print s.name, " = ", s.recent[:s.stop]

    y_stream = Stream('y')
    x_stream = Stream('x')
    z_stream = cumulative_sum_of_streams([x_stream, y_stream])
    z_stream.set_name('z')
    print_stream_recent(z_stream)

    y_stream.extend([3, 5])
    x_stream.extend([10])
    print_stream_recent(z_stream)

    y_stream.extend([2, 4])
    x_stream.extend([20, 30, 40, 50])
    print_stream_recent(z_stream)

if __name__ == '__main__':
    main()

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
def split_even_odd_stream(input_stream):
    # List function: list -> list of lists
    def split_even_odd_list(input_list):
        return [filter(lambda n: n%2 == 0, input_list), \
                filter(lambda n: n%2 != 0, input_list)]
    
    return stream_func(
        list_func=split_even_odd_list,
        inputs=input_stream,
        num_outputs=2,
        state=None,
        call_streams=None)



def main():
    def print_stream_recent(s):
        print s.name, " = ", s.recent[:s.stop]

    x_stream = Stream('x')
    y_stream, z_stream = split_even_odd_stream(x_stream)
    y_stream.set_name('y')
    z_stream.set_name('z')

    x_stream.extend([2, 4, 5, 1])
    print_stream_recent(y_stream)
    print_stream_recent(z_stream)

if __name__ == '__main__':
    main()

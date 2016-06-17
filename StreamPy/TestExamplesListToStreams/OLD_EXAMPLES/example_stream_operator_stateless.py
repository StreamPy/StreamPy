"""This module contains examples of the stateless single stream source
"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from ListOperators import stream_func

def f(input_list):
    return [v*v for v in input_list]

# Stream function
def stream_operator(input_stream, f):
    # List function: list -> list
    def list_operator(input_list):
        return f(input_list)
    return stream_func(
        list_func=list_operator,
        inputs=input_stream,
        num_outputs=1,
        state=None,
        call_streams=None)



def main():
    def print_stream_recent(s):
        print s.name, " = ", s.recent[:s.stop]

    y_stream = Stream('y stream')
    z_stream = stream_operator(y_stream, f)
    z_stream.set_name('z')
    print_stream_recent(z_stream)

    y_stream.extend([3, 5])
    print_stream_recent(z_stream)

    y_stream.extend([2, 4])
    print_stream_recent(z_stream)

if __name__ == '__main__':
    main()

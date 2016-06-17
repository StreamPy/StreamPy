"""This module contains examples of the stateless single stream source
"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from ListOperators import stream_func

def print_stream(input_stream):
    # List function: list -> ()
    def print_list(lst):
        for v in lst:
            print '{0} = {1}'.format(input_stream.name, v)

    return stream_func(
        list_func=print_list,
        inputs=input_stream,
        num_outputs=0,
        state=None,
        call_streams=None)



def main():
    y_stream = Stream('y_stream')
    print_stream(y_stream)
    y_stream.extend(range(10, 20, 2))
    y_stream.extend(range(40, 50, 2))
    
    

if __name__ == '__main__':
    main()

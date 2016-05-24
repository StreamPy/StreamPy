if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Stream import Stream, _no_value
from Operators import stream_func, stream_agent
import numpy as np

def main():

    def print_stream(stream):

        def print_list(lst):
            for v in lst:
                print 'from print_list {0} : {1}'.format(stream.name, v)

        return stream_agent(
            inputs=stream, f_type='list',
            f=print_list, outputs=None)

    def print_stream_elements(stream):

        def print_element(v):
            print 'from print_element {0} : {1}'.format(stream.name, v)

        return stream_func(
            inputs=stream,
            f_type='element',
            f=print_element,
            num_outputs=0)

   

    x = Stream('x')
    print_stream(x)

    x.extend([1, 2])
    x.print_recent()
    x.extend([0, 1, 3])
    x.print_recent()

if __name__ == '__main__':
    main()

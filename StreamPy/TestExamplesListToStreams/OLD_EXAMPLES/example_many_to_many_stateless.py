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
def outliers_and_inrange_streams(x_and_y_streams, a, b, delta):
    # List function: list of lists -> list of lists
    def outliers_and_inrange_lists(x_and_y_lists):
        z_list = zip(*x_and_y_lists)
        outliers_list = list(v for v in z_list if abs(a*v[0] + b - v[1]) > delta)
        inrange_list= list(v for v in z_list if abs(a*v[0] + b - v[1]) <= delta)
        return ([inrange_list, outliers_list])
    
    return stream_func(
        list_func=outliers_and_inrange_lists,
        inputs=x_and_y_streams,
        num_outputs=2,
        state=None,
        call_streams=None)



def main():
    def print_stream_recent(s):
        print s.name, " = ", s.recent[:s.stop]

    x_stream = Stream('x')
    y_stream = Stream('y')
    a = 1
    b = 0
    delta = 2
    inrange_stream, outliers_stream = \
      outliers_and_inrange_streams([x_stream, y_stream], a, b, delta)
    inrange_stream.set_name('in range')
    outliers_stream.set_name('outliers')

    x_stream.extend(range(5))
    y_stream.extend(range(2, 7, 1))
    print_stream_recent(x_stream)
    print_stream_recent(y_stream)
    print_stream_recent(inrange_stream)
    print_stream_recent(outliers_stream)

    x_stream.extend(range(5))
    y_stream.extend(range(6, 14, 1))
    print_stream_recent(x_stream)
    print_stream_recent(y_stream)
    print_stream_recent(inrange_stream)
    print_stream_recent(outliers_stream)
if __name__ == '__main__':
    main()

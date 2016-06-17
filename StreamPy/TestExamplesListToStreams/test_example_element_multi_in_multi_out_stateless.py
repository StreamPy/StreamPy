"""This module contains examples of stream_func where f_type
is 'element' and stream_func has a list of multiple input streams,
a single output stream, and the operation is stateless. These
examples must have a LIST of input streams and not a single
input stream.

The functions on static Python data structures are of the form:
    list -> element

"""

if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Stream import Stream, _no_value
from Operators import stream_func

from stream_test import *

    
def inrange_and_outlier_streams(list_of_streams,
                                 a, b, delta):
    
    def in_range_and_outlier_values(x_and_y):
        x, y = x_and_y
        if abs(a*x+b-y) > delta:
            # (x,y) is an outlier
            # The streams returned by stream func are:
            # [inrange stream, outlier stream]
            # Return _no_value for the inrange stream,
            # and return x_and_y for the outlier stream.
            return ([_no_value, x_and_y])
        else:
            # (x,y) is in range
            # Return _no_value for the outlier stream,
            # and return x_and_y for the in range stream.
            return ([x_and_y, _no_value])

    return stream_func(inputs=list_of_streams,
                       f_type='element',
                       f=in_range_and_outlier_values,
                       num_outputs=2)

def test():
        

    # Create stream x, and give it name 'x'.
    x = Stream('input_0')
    y = Stream('input_1')

    
    inrange_stream, outlier_stream = \
      inrange_and_outlier_streams(
          list_of_streams=[x,y],
          a=2, b=1, delta=2)

    # Give names to streams.
    # This is helpful in reading output.
    inrange_stream.set_name('inrange')
    outlier_stream.set_name('outlier')

    check(inrange_stream, [(3, 7), (4, 10), (6, 12), (6, 14)])
    check(outlier_stream, [(5, 14), (8, 2), (2, 9), (4, 2), (2, 8)])

    print
    # Add values to the tail of stream x.
    x.extend([3, 5, 8])
    y.extend([7, 14])

    # Print recent values of the streams
    print 'Recent values of input streams'
    x.print_recent()
    y.print_recent()

    print
    print 'Recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    # Add more values to the tail of stream x.
    x.extend([4, 6, 2])
    y.extend([2, 10, 12, 9])

    # Print recent values of the streams
    print
    print 'Recent values of input streams'
    x.print_recent()
    y.print_recent()

    print
    print 'Recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    # Add more values to the tail of stream x.
    x.extend([4, 6, 2])
    y.extend([2, 14, 8, 9])

    # Print recent values of the streams
    print
    print 'Recent values of input streams'
    x.print_recent()
    y.print_recent()

    print    
    print 'Recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    check_empty()


if __name__ == '__main__':
    test()


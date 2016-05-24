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
import numpy as np

from stream_test import *


# Code for function f in the diagram.
def sum_and_diff_streams(a_stream, b_stream):

    # Functions: list -> list
    def sum_and_diff_lists(a_and_b_lists):
        a_list, b_list = a_and_b_lists
        a_array, b_array = np.array(a_list), np.array(b_list)
        return [a_array+b_array, a_array-b_array]
        
    return stream_func(
        inputs=[a_stream, b_stream],
        f_type='list',
        f=sum_and_diff_lists,
        num_outputs=2)


# Code for function g in the diagram.
def sum_streams(c_stream, d_stream):
    def sum_lists(lists):
        c_list, d_list = lists
        return [c_list[i]+d_list[i] for i in range(len(c_list))]
    
    return stream_func(
        inputs=[c_stream, d_stream],
        f_type='list',
        f=sum_lists,
        num_outputs=1)

def h(a_stream, b_stream, d_stream):
    x_stream, y_stream = \
      sum_and_diff_streams(a_stream, b_stream)
    z_stream = sum_streams(y_stream, d_stream)
    return [x_stream, z_stream]
    
    

# Functions: stream -> stream.
# The n-th element of the output stream is f() applied to the n-th
# elements of each of the input streams.
# Function mean is defined above, and functions sum and max are the
# standard Python functions.
## inrange_and_outlier_streams = partial(stream_func, f_type='list',
##                                      f=inrange_and_outlier,
##                                      num_outputs=2)

def test():

    # Create stream x, and give it name 'x'.
    a_stream = Stream('a_stream')
    b_stream = Stream('b_stream')
    d_stream = Stream('d_stream')

    
    x_stream, z_stream = h(a_stream, b_stream, d_stream)

    # Give names to streams u, v, and w. This is helpful in reading output.
    x_stream.set_name('x_stream')
    z_stream.set_name('z_stream')

    check(x_stream, [17, 12, 19, 111, 0, 20, 102, 64, 12, 15])
    check(z_stream, [8, 4, 7, -39, 0, 10, 110, 40, 14, -3])

    print
    # Add values to the tail of stream x.
    a_stream.extend([8, 5, 8, 11, 0, 10, 100, 50])
    b_stream.extend([9, 7, 11, 100, 0, 10])
    d_stream.extend([9, 6, 10, 50, 0, 10])

    # Print recent values of the streams
    print 'recent values of input streams'
    a_stream.print_recent()
    b_stream.print_recent()
    d_stream.print_recent()


    print 'recent values of output streams'
    x_stream.print_recent()
    z_stream.print_recent()

    print
    # Add more values to the tail of stream x.
    a_stream.extend([4, 6, 2])
    b_stream.extend([2, 14, 8, 9])
    d_stream.extend([12, 4, 18, 0])    


    # Print recent values of the streams
    print 'recent values of input streams'
    a_stream.print_recent()
    b_stream.print_recent()
    d_stream.print_recent()

    print 'recent values of output streams'
    x_stream.print_recent()
    z_stream.print_recent()

    check_empty()


if __name__ == '__main__':
    test()


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


def inrange_and_outlier_streams(x_and_y_streams, a, b, delta):

    # Functions: list -> list
    def inrange_and_outlier(x_and_y_lists):
        z_list = zip(*x_and_y_lists)
        outliers_list = [v for v in z_list if abs(a*v[0] + b -v[1]) > delta]
        inrange_list= [v for v in z_list if abs(a*v[0] + b -v[1]) <= delta]
        return ([inrange_list, outliers_list])

    return stream_func(
        inputs=x_and_y_streams, f_type='list',
        f=inrange_and_outlier, num_outputs=2)

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
    x = Stream('input_0')
    y = Stream('input_1')

    
    inrange_stream, outlier_stream = inrange_and_outlier_streams(
        x_and_y_streams=[x,y], a=1, b=0, delta=3)

    # Give names to streams u, v, and w. This is helpful in reading output.
    inrange_stream.set_name('inrange')
    outlier_stream.set_name('outlier')

    check(inrange_stream, [(8, 9), (5, 7), (6, 8), (4, 2)])
    check(outlier_stream, [(8, 2), (4, 14), (2, 9), (6, 14), (2, 8)])

    print
    # Add values to the tail of stream x.
    x.extend([8, 5, 8])
    y.extend([9, 7])

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()

    print 'recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    print
    print 'Adding [4, 6, 2], [2, 3, 8], [5, 3, 0, -1] to 3 input streams'
    # Add more values to the tail of stream x.
    x.extend([4, 6, 2])
    y.extend([2, 14, 8, 9])


    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()

    print 'recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    print
    print 'Adding [4, 6, 2], [2, 3, 8], [5, 3, 0, -1] to 3 input streams'
    # Add more values to the tail of stream x.
    x.extend([4, 6, 2])
    y.extend([2, 14, 8, 9])


    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()

    print 'recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    check_empty()


if __name__ == '__main__':
    test()


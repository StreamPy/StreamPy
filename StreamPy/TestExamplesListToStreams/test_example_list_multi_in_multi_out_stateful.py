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


def inrange_and_outlier_streams(x_and_y_streams, a, b, delta):

    def inrange_and_outlier(x_and_y_lists, state):
        num_inrange, num_outliers = state
        z_list = zip(*x_and_y_lists)
        inrange_list, outliers_list = [], []
        for v in z_list:
            if abs(a*v[0] + b -v[1]) > delta:
                # outlier
                num_outliers += 1
                percentage_outliers = num_outliers/float(num_outliers+num_inrange)
                outliers_list.append((v, percentage_outliers))
            else:
                # in range
                num_inrange += 1
                percentage_outliers = num_outliers/float(num_outliers+num_inrange)
                inrange_list.append((v, percentage_outliers))
                
        state = num_inrange, num_outliers
        return ([inrange_list, outliers_list], state)

    return stream_func(
        inputs=x_and_y_streams, f_type='list',
        f=inrange_and_outlier, num_outputs=2,
        state=(0,0))

def test():

    x = Stream('input_0')
    y = Stream('input_1')

    
    inrange_stream, outlier_stream = inrange_and_outlier_streams(
        x_and_y_streams=[x,y], a=1, b=0, delta=3)
    
    inrange_stream.set_name('inrange')
    outlier_stream.set_name('outlier')

    check(inrange_stream, [((3, 4), 0.0), ((8, 8), 1.0 / 3.0), ((12, 12), 0.4)])
    check(outlier_stream, [((5, 9), 0.5), ((10, 15), 0.5), ((21, 11), 0.5)])

    print
    # Add values to the tail of stream x.
    x.extend([3, 5, 8, 10])
    y.extend([4, 9, 8, 15])

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()

    print 'recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    print
    # Add more values to the tail of stream x.
    x.extend([12, 21, 13])
    y.extend([12, 11])

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


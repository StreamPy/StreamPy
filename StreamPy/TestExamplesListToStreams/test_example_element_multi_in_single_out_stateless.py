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


# Functions: list -> element
def mean(list_of_numbers):
    return sum(list_of_numbers)/float(len(list_of_numbers))

def large_max(list_of_numbers):
    if max(list_of_numbers) > 2*mean(list_of_numbers):
        return list_of_numbers
    else:
        return _no_value

# Functions: stream -> stream.
# The n-th element of the output stream is f() applied to the n-th
# elements of each of the input streams.
# Function mean is defined above, and functions sum and max are the
# standard Python functions.
stream_sum = partial(stream_func, f_type='element', f=sum, num_outputs=1)
stream_max = partial(stream_func, f_type='element', f=max, num_outputs=1)    
stream_mean = partial(stream_func, f_type='element', f=np.mean, num_outputs=1)
stream_large_max = partial(stream_func, f_type='element', f=large_max, num_outputs=1)    

def test():
    # Create stream x, and give it name 'x'.
    x = Stream('input_0')
    y = Stream('input_1')
    z = Stream('input_2')

    # u is the stream returned by stream_sum([x,y])  and
    # v is the stream returned by stream_max([x,y])
    # w is the stream returned by stream_mean([x,y]).
    # u[i] = sum(x[i],y[i])
    # v[i] = max(x[i],y[i])
    # w[i] = mean(x[i],y[i])    
    u = stream_sum([x,y,z])
    v = stream_max([x,y,z])
    w = stream_mean([x,y,z])
    a = stream_large_max([x,y,z])


    # Give names to streams u, v, and w. This is helpful in reading output.
    u.set_name('sum of inputs')
    v.set_name('max of inputs')
    w.set_name('mean of inputs')
    a.set_name('max if at least twice mean')

    check(u, [6, 15, 15, 9, 9, 9])
    check(v, [3, 7, 8, 4, 6, 8])
    check(w, [2.0, 5.0, 5.0, 3.0, 3.0, 3.0])
    check(a, [(2, 8, -1)])

    print
    print 'Adding [3, 5, 8], [1, 7, 2], [2, 3] to 3 input streams'
    # Add values to the tail of stream x.
    x.extend([3, 5, 8])
    y.extend([1, 7, 2])
    z.extend([2, 3])

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print 'recent values of output streams'
    u.print_recent()
    v.print_recent()
    w.print_recent()
    a.print_recent()

    print
    print 'Adding [4, 6, 2], [2, 3, 8], [5, 3, 0, -1] to 3 input streams'
    # Add more values to the tail of stream x.
    x.extend([4, 6, 2])
    y.extend([2, 3, 8])
    z.extend([5, 3, 0, -1])

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print 'recent values of output streams'
    u.print_recent()
    v.print_recent()
    w.print_recent()
    a.print_recent()

    check_empty()


if __name__ == '__main__':
    test()


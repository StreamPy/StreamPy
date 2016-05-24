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


# Functions: list of lists -> list
def mean_multilist(multilist):
    return np.mean(np.array(multilist), axis=0)

def average(a, state):
    n, cum = state
    b = np.zeros(len(a)+1)
    b[0] = cum
    b[1:] = a
    b = np.cumsum(b)
    n_array = np.arange(n, n+len(b), 1)
    c = b[1:]/np.rint(n_array[1:])
    state = (n_array[-1], b[-1])
    return (c, state)

def average_of_running_means(list_of_numbers, state):
    return average(mean_multilist(list_of_numbers), state)

# Functions: stream -> stream.
# The n-th element of the output stream is f() applied to the n-th
# elements of each of the input streams.
# Function mean is defined above, and functions sum and max are the
# standard Python functions.
## stream_running_mean = partial(stream_func, f_type='element',
##                               f=average_of_running_means, num_outputs=1,
##                               state = (0,0.0))
stream_running_mean = \
  partial(stream_func,
          f_type='list',
          f=average_of_running_means,
          num_outputs=1,
          state = (0,0.0))

stream_mean = partial(stream_func, f_type='list',
                              f=mean_multilist, num_outputs=1)

def test():
    
    # Create stream x, and give it name 'x'.
    x = Stream('input_0')
    y = Stream('input_1')
    z = Stream('input_2')

    u = stream_running_mean([x,y,z])
    w = stream_mean([x,y,z])

    # Give names to streams. This is helpful in reading output.
    u.set_name('running mean of inputs')
    w.set_name('mean of inputs')

    check(u, [2.0, 3.5, 4.0, 3.75, 3.6, 3.5])
    check(w, [2.0, 5.0, 5.0, 3.0, 3.0, 3.0])

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
    w.print_recent()

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
    w.print_recent()

    check_empty()


if __name__ == '__main__':
    test()


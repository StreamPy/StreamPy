"""This module contains examples of stream_func where f_type
is 'element' and stream_func has a single input stream, a
single output stream, and the operation is stateless.

The functions on static Python data structures are of the form:
    element -> element

"""
if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Stream import Stream, StreamArray, _no_value
from Operators import stream_func
import numpy as np

from stream_test import *

    
# Functions: list, state -> list, state
def cumulative(a, state):
    b = np.zeros(len(a)+1)
    b[0] = state
    b[1:] = a
    b = np.cumsum(b)
    return (b[1:], b[-1])

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
    

stream_cumulative = partial(stream_func, f_type='list', f=cumulative,
                            num_outputs=1, state=0.0)
stream_average = partial(stream_func, f_type='list', f=average,
                            num_outputs=1, state=(0,0.0))

def test():    

    # Create stream x and give it names 'x'.
    x = StreamArray('input')

    # v is the stream returned by stream_cumulative(x)  and
    v = stream_cumulative(x)
    # avg is the stream returned by stream_average(x)
    avg = stream_average(x)

    # Give names to streams. This is helpful in reading output.
    v.set_name('cumulative sum of input')
    avg.set_name('average of input')

    check(v, [3.0, 8.0, 18.0, 20.0, 25.0, 36.0])
    check(avg, [3.0, 4.0, 6.0, 5.0, 5.0, 6.0])

    print
    print 'add values [3, 5, 10] to the tail of the input stream.'
    # Add values to the tail of stream x.
    x.extend([3, 5, 10])

    # Print the N most recent values of streams x, v, w.
    x.print_recent()
    v.print_recent()
    avg.print_recent()

    print
    print 'add values [2, 5, 11] to the tail of the input stream.'
    # Add more values to the tail of stream x.
    x.extend([2, 5, 11])

    # Print the N most recent values of streams x, v, w.
    x.print_recent()
    v.print_recent()
    avg.print_recent()

    check_empty()


if __name__ == '__main__':
    test()

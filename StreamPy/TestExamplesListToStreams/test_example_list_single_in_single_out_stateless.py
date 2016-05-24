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
from Stream import Stream, _no_value
from Operators import stream_func

from stream_test import *


# Functions: list -> list
def square(lst):
    return [v*v for v in lst]

def double(lst):
    return [2*v for v in lst]

def even(lst):
    return [v for v in lst if not v%2]

# Functions: stream -> stream.
# Each element of the output stream is f() applied to the corresponding
# element of the input stream.
stream_square = partial(stream_func, f_type='list', f=square, num_outputs=1)
stream_double = partial(stream_func, f_type='list', f=double, num_outputs=1)
stream_even = partial(stream_func, f_type='list', f=even, num_outputs=1)


def test():

    # Create stream x, and give it name 'x'.
    x = Stream('input')

    # u is the stream returned by stream_square(x)  and
    # v is the stream returned by stream_double(x)
    # w is the stream returned by stream_square(v) and
    #   so w could have been defined as:
    #   stream_square(stream_double(x))
    # a is the stream containing only even values of x
    u = stream_square(x)
    v = stream_double(x)
    w = stream_square(v)
    a = stream_even(x)

    # Give names to streams u, v, and w. This is helpful in reading output.
    u.set_name('square of input')
    v.set_name('double of input')
    w.set_name('square of double of input')
    a.set_name('even values in input')

    check(u, [9, 25, 4, 36])
    check(v, [6, 10, 4, 12])
    check(w, [36, 100, 16, 144])
    check(a, [2, 6])

    print
    print 'add [3, 5] to the tail of the input stream'
    # Add values to the tail of stream x.
    x.extend([3, 5])

    # Print the N most recent values of streams x, u, v, w.
    x.print_recent()
    u.print_recent()
    v.print_recent()
    w.print_recent()
    a.print_recent()    

    print
    print 'add [2, 6] to the tail of the input stream'
    # Add more values to the tail of stream x.
    x.extend([2, 6])

    # Print the N most recent values of streams x, u, v, w.
    x.print_recent()
    u.print_recent()
    v.print_recent()
    w.print_recent()
    a.print_recent()

    check_empty()

if __name__ == '__main__':
    test()


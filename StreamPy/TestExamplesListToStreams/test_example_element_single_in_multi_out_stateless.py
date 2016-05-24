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


# Functions: element -> list
def even_odd(n):
    if n%2:
        # since n is odd, the zero-th element is
        # _no_value, and the first element is n
        # in the returned list
        return [_no_value, n]
    else:
        # since n is even, the zero-th element is
        # n, and the first element is _no_value
        # in the returned list.            
        return [n, _no_value]

# Functions: stream -> stream.
# The n-th element of the output stream is f() applied to the n-th
# elements of each of the input streams.
# Function mean is defined above, and functions sum and max are the
# standard Python functions.
stream_even_odd = partial(stream_func, f_type='element', f=even_odd, num_outputs=2)


def test():

    # Create stream x, and give it name 'x'.
    x = Stream('input_0')

    # u is the stream returned by stream_sum([x,y])  and
    # v is the stream returned by stream_max([x,y])
    # w is the stream returned by stream_mean([x,y]).
    # u[i] = sum(x[i],y[i])
    # v[i] = max(x[i],y[i])
    # w[i] = mean(x[i],y[i])    
    evens, odds = stream_even_odd(x)

    # Give names to streams u, v, and w. This is helpful in reading output.
    evens.set_name('even numbers in x')
    odds.set_name('odd numbers in x')

    check(evens, [8, 4, 6, 2])
    check(odds, [3,5])

    print
    print 'Adding [3, 5, 8], [1, 7, 2], [2, 3] to 3 input streams'
    # Add values to the tail of stream x.
    x.extend([3, 5, 8])

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()

    print 'recent values of output streams'
    evens.print_recent()
    odds.print_recent()


    print
    print 'Adding [4, 6, 2], [2, 3, 8], [5, 3, 0, -1] to 3 input streams'
    # Add more values to the tail of stream x.
    x.extend([4, 6, 2])

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()

    print 'recent values of output streams'
    evens.print_recent()
    odds.print_recent()

    check_empty()


if __name__ == '__main__':
    test()


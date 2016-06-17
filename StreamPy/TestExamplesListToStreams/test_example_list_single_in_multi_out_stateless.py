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


# Functions: list -> list of lists
def even_odd(list_of_integers):
    evens_list = [n for n in list_of_integers if not n%2]
    odds_list = [n for n in list_of_integers if n%2]
    return (evens_list, odds_list)

# Functions: stream -> stream.
# The n-th element of the output stream is f() applied to the n-th
# elements of each of the input streams.
# Function mean is defined above, and functions sum and max are the
# standard Python functions.
stream_even_odd = partial(stream_func, f_type='list',
                          f=even_odd, num_outputs=2)


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
    check(odds, [3, 5, 1])

    print
    print 'Adding [3, 5, 8] to input stream'
    # Add values to the tail of stream x.
    x.extend([3, 5, 8])

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()

    print 'recent values of output streams'
    evens.print_recent()
    odds.print_recent()


    print
    print 'Adding [4, 6, 2, 1] to the input stream'
    # Add more values to the tail of stream x.
    x.extend([4, 6, 2, 1])

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()

    print 'recent values of output streams'
    evens.print_recent()
    odds.print_recent()

    check_empty()


if __name__ == '__main__':
    test()


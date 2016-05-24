"""This module contains examples of stream_func where f_type
is 'element' and stream_func has a single input stream, and
a single output stream, and the operation is stateful.

The state captures information in the past input streams;
this information is required to append values to the tails
of the output streams.

The functions on static Python data structures are of the form:
    element, state -> element, state
These functions typically have the following structure:
(1) Extract variables from the state.
(2) Compute the output and the new state.
(3) Return (output, new_state)

"""
if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Stream import Stream
from Operators import stream_func

from stream_test import *


# Functions: element, state -> element, state
def cumulative_sum(v, cumulative):
    """ This function is used to output a stream
    where the n-th value on the output stream is
    the cumulative sum of the first n values of the
    input stream.
    
    The state of the input stream is cumulative.
    When used to create a stream, cumulative is
    the sum of all the values in the input stream
    received so far.
    v is the next value received in the input stream.
    
    """
    cumulative += v
    return (cumulative, cumulative)

def average(v, state):
    """ This function is used to output a stream
    where the n-th value on the output stream is
    the average of the first n values of the
    input stream.
    
    The state of the input stream is the pair (n,cum).
    When used to create a stream, n is the number
    of values received on the input stream, and cum
    is the sum of all the values in the input stream
    received so far.
    v is the next value received in the input stream.
    
    """
    n, cum = state
    n += 1
    cum += v
    mean = cum/float(n)
    state = (n, cum)
    return (mean, state)
    

# Functions: stream -> stream.
# Each element of the output stream is f() applied to the corresponding
# element of the input stream.
stream_cumulative = partial(stream_func, f_type='element', f=cumulative_sum,
                            num_outputs=1, state=0)
stream_average = partial(stream_func, f_type='element', f=average,
                            num_outputs=1, state=(0,0.0))

def test():

    # Create stream x and give it names 'x'.
    x = Stream('input')

    # v is the stream returned by stream_cumulative(x)  and
    # w is the stream returned by stream_cumulative(v).
    v = stream_cumulative(x)
    w = stream_cumulative(v)
    # avg is the stream returned by stream_average(x)
    avg = stream_average(x)

    # Give names to streams. This is helpful in reading output.
    v.set_name('cumulative sum of input')
    w.set_name('cumulative sum of cumulative sum of input')
    avg.set_name('average of input')

    check(v, [3, 8, 18, 20, 25, 36])
    check(w, [3, 11, 29, 49, 74, 110])
    check(avg, [3.0, 4.0, 6.0, 5.0, 5.0, 6.0])

    print
    print 'add values [3, 5, 10] to the tail of the input stream.'
    # Add values to the tail of stream x.
    x.extend([3, 5, 10])

    # Print the N most recent values of streams x, v, w.
    x.print_recent()
    v.print_recent()
    w.print_recent()
    avg.print_recent()

    print
    print 'add values [2, 5, 11] to the tail of the input stream.'
    # Add more values to the tail of stream x.
    x.extend([2, 5, 11])

    # Print the N most recent values of streams x, v, w.
    x.print_recent()
    v.print_recent()
    w.print_recent()
    avg.print_recent()

    check_empty()
    

if __name__ == '__main__':
    test()


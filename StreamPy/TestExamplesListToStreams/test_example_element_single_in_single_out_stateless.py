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
from Stream import Stream
from Stream import _no_value
from Operators import stream_func

from stream_test import *

def print_stream(stream):
    stream_name = stream.name

    def print_stream_value(v):
        print stream_name, ':', 'next value=', v

    return stream_func(
        inputs=stream,
        f_type='element',
        f=print_stream_value,
        num_outputs=1)


# Functions: element -> element
def square(v):
    return v*v

def double(v):
    return 2*v

def even(v):
    if not v%2:
        return v
    else:
        return _no_value

def square_elements_in_stream(stream):
    return stream_func(stream, f_type='element', f=square, num_outputs=1)

# Examples illustrating how to wrap a function on elements to obtain
# a function on streams using 'def'
# Function on streams
def multiply_elements_in_stream(stream, multiplier):

    # function on an element that returns an element
    def mult(v):
        return multiplier*v

    # Use the stream_func wrapper to return a function on streams.
    return stream_func(inputs=stream, f_type='element', f=mult, num_outputs=1)


# Function on streams
def boolean_of_values_greater_than_threshold(stream, threshold):

    # function on an element that returns an element
    def value_greater_than_threshold(value):
        return value > threshold

    # Use the stream_func wrapper to return a function on streams.
    return stream_func(
        inputs=stream,
        f_type='element',
        f=value_greater_than_threshold,
        num_outputs=1)
    
# Functions: stream -> stream.
# Each element of the output stream is f() applied to the corresponding
# element of the input stream.
# These examples illustrate the use of the wrapper 'stream_func' with
# 'partial' to wrap functions (square, double, even) on elements to
# obtain functions (stream_square, stream_double, stream_even) on streams.
stream_square = partial(stream_func, f_type='element', f=square, num_outputs=1)
stream_double = partial(stream_func, f_type='element', f=double, num_outputs=1)
stream_even = partial(stream_func, f_type='element', f=even, num_outputs=1)


def test():
    

    # Create stream x, and give it name 'input'.
    x = Stream('input')

    # u is the stream returned by stream_square(x)  and
    # v is the stream returned by stream_double(x)
    # w is the stream returned by stream_square(v) and
    #   so w could have been defined as:
    #   stream_square(stream_double(x))
    # a is the stream containing only even values of x
    #   Function even(v) may return _no_value, but
    #   _no_value is not inserted into the stream.
    #   Thus even(v) acts like a filter.
    print_stream(x)
    r = square_elements_in_stream(x)
    u = stream_square(x)
    v = stream_double(x)
    w = stream_square(v)
    a = stream_even(x)
    b = multiply_elements_in_stream(stream=x, multiplier=3)
    c = boolean_of_values_greater_than_threshold(
        stream=x, threshold=4)
    

    # Give names to streams u, v, and w. This is helpful in reading output.
    r.set_name('r: square of input')
    u.set_name('u: square of input')
    v.set_name('double of input')
    w.set_name('square of double of input')
    a.set_name('even values in input')
    b.set_name('multiply values in input')
    c.set_name('booleans where value exceeds threshold')

    check(r, [9, 25, 4, 36])
    check(u, [9, 25, 4, 36])
    check(v, [6, 10, 4, 12])
    check(w, [36, 100, 16, 144])
    check(a, [2, 6])
    check(b, [9, 15, 6, 18])
    check(c, [False, True, False, True])

    print
    print 'add [3, 5] to the tail of the input stream'
    # Add values to the tail of stream x.
    x.extend([3, 5])

    # Print the N most recent values of streams x, u, v, w.
    x.print_recent()
    r.print_recent()
    u.print_recent()
    v.print_recent()
    w.print_recent()
    a.print_recent()
    b.print_recent()
    c.print_recent()

    print
    print 'add [2, 6] to the tail of the input stream'
    # Add more values to the tail of stream x.
    x.extend([2, 6])

    # Print the N most recent values of streams x, u, v, w.
    x.print_recent()
    r.print_recent()
    u.print_recent()
    v.print_recent()
    w.print_recent()
    a.print_recent()
    b.print_recent()
    c.print_recent()

    x.close()
    r.close()
    u.close()

    check_empty()

if __name__ == '__main__':
    test()


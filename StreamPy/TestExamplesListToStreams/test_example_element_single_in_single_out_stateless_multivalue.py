if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Stream import Stream
from Stream import _no_value
from Stream import _multivalue
from Operators import stream_func

from stream_test import *


def f(v):
    if not v%2:
        return _multivalue([v/2, v])
    else:
        return v

def g(stream):
    return stream_func(inputs=stream,
                       f_type='element',
                       f=f,
                       num_outputs=1)

def test():

    # Create stream x, and give it name 'input'.
    x = Stream('input')
    y = g(x)
    y.set_name('output')

    check(y, [3, 1, 2, 5, 2, 4, 7])

    # Add values 3, 2, 5 to the tail of stream x.
    x.extend([3, 2, 5])
    x.print_recent()
    y.print_recent()

    # Add values 4, 7 to the tail of stream x.
    x.extend([4, 7])
    x.print_recent()
    y.print_recent()

    check_empty()

if __name__ == '__main__':
    test()

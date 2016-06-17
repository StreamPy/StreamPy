if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Stream import Stream, StreamArray
from Stream import _no_value
from Operators import stream_func

from stream_test import *


def square(v):
    return v*v

def square_stream_when_clock_ticks(
        input_stream, trigger_stream):
    
    return stream_func(inputs=input_stream,
                       f_type='element',
                       f=square,
                       num_outputs=1,
                       call_streams=[trigger_stream]
                       )


def test():

    x = Stream('x')
    a = StreamArray('a')
    clock_ticks = Stream('clock')
    y = square_stream_when_clock_ticks(
        input_stream=x, trigger_stream=clock_ticks)
    z = square_stream_when_clock_ticks(
        input_stream=a, trigger_stream=clock_ticks)
    y.set_name('y')
    z.set_name('z')

    check(y, [9, 25, 4, 16])
    check(z, [9.0, 25.0, 4.0, 16.0])

    x.extend([3, 5])
    a.extend([3, 5])
    x.print_recent()
    a.print_recent()
    clock_ticks.print_recent()
    y.print_recent()
    z.print_recent()

    print
    x.extend([2, 4])
    a.extend([2, 4])
    x.print_recent()
    a.print_recent()
    clock_ticks.print_recent()
    y.print_recent()
    z.print_recent()

    print
    clock_ticks.extend(['tick'])
    x.print_recent()
    a.print_recent()
    clock_ticks.print_recent()
    y.print_recent()
    z.print_recent()

    print
    clock_ticks.extend(['tick'])
    x.print_recent()
    a.print_recent()
    clock_ticks.print_recent()
    y.print_recent()
    z.print_recent()

    check_empty()

if __name__ == '__main__':
    test()

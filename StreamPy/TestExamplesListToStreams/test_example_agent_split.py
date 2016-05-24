if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Stream import Stream
from Stream import _no_value
from Operators import stream_func, stream_agent

from stream_test import *

def number_even_odd(m):
    if m%2:
        return [_no_value, m]
    else:
        return [m, _no_value]

def test():
    in_1 = Stream(name='in_1')
    out_1 = Stream(name='out_1')
    out_2 = Stream(name= 'out_2')

    check(out_1, [4, 8])
    check(out_2, [3, 5])

    stream_agent(
        inputs=in_1,
        outputs=[out_1, out_2],
        f_type='element',
        f=number_even_odd)
    in_1.extend([3, 4, 5, 8])
    out_1.print_recent()
    out_2.print_recent()

    check_empty()

if __name__ == '__main__':
    test()

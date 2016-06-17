
if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Stream import Stream
from Stream import _no_value
from Operators import stream_func, stream_agent

from stream_test import *

def test():
    in_1 = Stream(name='in_1')
    in_2 = Stream(name='in_2')
    out_1 = Stream(name='out_1')
    out_2 = Stream(name= 'out_2')

    check(out_1, [16, 18, 20])
    stream_agent(
        inputs=[in_1, in_2],
        outputs=out_1,
        f_type='element',
        f=sum)
    in_1.extend([3, 4, 5])
    in_2.extend([13, 14, 15])
    out_1.print_recent()

    check_empty()

if __name__ == '__main__':
    test()

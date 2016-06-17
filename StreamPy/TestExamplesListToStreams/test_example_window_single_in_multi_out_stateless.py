if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Stream import Stream 
from Operators import stream_func
import numpy as np

from stream_test import *


def max_and_min(lst):
    return (max(lst), min(lst))

max_min_of_windows_in_stream = \
  partial(stream_func,
          f_type='window',
          f=max_and_min,
          num_outputs=2,
          window_size=2,
          step_size=2)

def test():

    x = Stream('x')

    y,z = max_min_of_windows_in_stream(x)

    y.set_name('y')
    z.set_name('z')

    check(y, [5])
    check(z, [3])
    
    x.extend([3,5])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print

    x.extend([11,15])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print

    check_empty()

if __name__ == '__main__':
    test()

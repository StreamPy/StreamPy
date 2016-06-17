if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from functools import partial
from Stream import Stream 
from Operators import stream_func
import numpy as np

from stream_test import *


def diff_of_means(list_of_two_lists):
    a, b = list_of_two_lists
    return np.mean(a) - np.mean(b)

diff_means_of_windows_in_streams = \
  partial(stream_func,
          f_type='window',
          f=diff_of_means,
          num_outputs=1,
          window_size=2,
          step_size=2)

def test():
    
    x = Stream('x')
    y = Stream('y')


    z = diff_means_of_windows_in_streams([x,y])
    
    z.set_name('z')

    check(z, [1.0])
    
    x.extend([3,5])
    y.extend([2])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print

    x.extend([11,15])
    y.extend([4, -10, -12])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print

    check_empty()

if __name__ == '__main__':
    test()


if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Stream import Stream 
from Operators import stream_func
import numpy as np

from stream_test import *


def exp_smoothing_mean_std(lst, state):
    alpha = 0.8
    a = np.array(lst)
    m, s = state
    m = (1-alpha)*m + alpha*a.mean()
    s = (1-alpha)*s + alpha*a.std()
    state = (m,s)
    return ([m,s], state)

exp_smooth_max_and_std_of_windows_in_stream = \
  partial(stream_func,
          f_type='window',
          f=exp_smoothing_mean_std,
          num_outputs=2,
          state=(0.0, 0.0),
          window_size=3,
          step_size=3)

def test():

    x = Stream('x')

    y,z = exp_smooth_max_and_std_of_windows_in_stream(x)

    y.set_name('y')
    z.set_name('z')

    check(y, [1.6000000000000001, 4.3200000000000003])
    check(z, [0.65319726474218087, 0.78383671769061702])
    
    x.extend([1, 2, 3, 4, 5])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print

    x.extend([6, 12, 13, 14, 15])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    print

    check_empty()

if __name__ == '__main__':
    test()

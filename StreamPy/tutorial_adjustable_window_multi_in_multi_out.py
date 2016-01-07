from Stream import Stream
from Operators import awf
from examples_element_wrapper import print_stream
import numpy as np
from random import randint
""".

"""

u = Stream('u')
v = Stream('v')
y = Stream('avg')
z = Stream('std')
a = Stream('call stream')
#print_stream(u)
#print_stream(v)
print_stream(y)
print_stream(z)

def h(list_of_windows, window_size, step_size,
      ratio, min_window_size):
    avg = np.mean([np.mean(window) for window in list_of_windows])
    std = np.mean([np.std(window) for window in list_of_windows])
    if std > ratio * avg:
        window_size += 1
        step_size += 1
    elif window_size > min_window_size:
        window_size -= 1
        step_size -= 1

    print 'std/avg = ', std/avg, 'window_size = ', window_size
    return ([avg, std], window_size, step_size)

initial_window_size = 6
initial_step_size = 6

awf([u,v], [y,z], h, initial_window_size, initial_step_size,
    call_streams=[a], ratio=0.6, min_window_size=4)

u.extend([randint(0, 20) for _ in range(15)])
v.extend([randint(0, 20) for _ in range(15)])
print 'UNPROCESSED INPUT \n'
# Agent does not execute though it has unprocessed input.

u.extend([randint(0, 20) for _ in range(15)])
v.extend([randint(0, 20) for _ in range(15)])
print 'MORE UNPROCESSED INPUT \n'
print 'INPUT IS PROCESSED WHEN VALUE APPEARS IN CALL STREAM.'
a.append(1)
# Agent processes unprocessed input.

u.extend([randint(0, 20) for _ in range(15)])
v.extend([randint(0, 20) for _ in range(15)])
print '\n MORE UNPROCESSED INPUT \n'
# Agent does not execute though it has unprocessed input.
print 'INPUT IS PROCESSED WHEN NEXT VALUE APPEARS IN CALL STREAM.'
a.append(2)
# Agent processes unprocessed input.


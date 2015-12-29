from Stream import Stream
from Operators import stream_agent, wf
from examples_element_wrapper import print_stream
import numpy as np
from random import randint
"""Simple example of the window function wf with
window size and step size of 3. Output is the mean
of the clipped window with a_min=9, a_max=11. These
values are used in this example so that you can
check the results easily.

"""

u = Stream('u')
v = Stream('v')
y = Stream('y')
print_stream(u)
print_stream(v)
print_stream(y)

def h(list_of_lists):
    return max([np.std(lst) for lst in list_of_lists])

wf([u, v], y, h, 5, 5)

u.extend([randint(0, 20) for _ in range(21)])
v.extend([randint(0, 20) for _ in range(25)])

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

x = Stream('x')
y = Stream('y')
print_stream(x)
print_stream(y)

def h(lst, a_min, a_max):
    return np.mean(np.clip(lst, a_min, a_max))
wf(x, y, h, 3, 3, a_min=9, a_max=11)

x.extend([randint(0, 20) for _ in range(20)])

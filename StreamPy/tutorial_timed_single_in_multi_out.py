from Stream import Stream, TimeAndValue
from Operators import stream_agent, tf
from examples_element_wrapper import print_stream
import numpy as np
from random import randint
from Stream import _no_value
"""Simple example of the window function wf with
window size and step size of 3. Output is the mean
of the clipped window with a_min=9, a_max=11. These
values are used in this example so that you can
check the results easily.

"""

x = Stream('x')
y = Stream('y')
z = Stream('z')
print_stream(x)
print_stream(y)
print_stream(z)

def h(timed_window, threshold):
    v = sum([w[1] for w in timed_window])
    if v > threshold: return (v, 0)
    else: return (0, v)

tf(x, [y,z], h, 10, 10, threshold=20)

x.extend([(2, 10), (6, 11), (12, 12), (14, 13), (19, 12), (22, 13), (49, 23), (51, 33)]) 

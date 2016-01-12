from Stream import Stream, TimeAndValue
from Operators import stream_agent, tf, stream_func, ef
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
class tv(object):
    def __init__(self, time, value):
        self.time = time
        self.value = value

def print_stream_tv(stream):
    def print_element(v, count):
        print '{0}[{1}] time = {2}, value = {3}'.format(stream.name, count, v.time, v.value)
        return (count+1)

    ef(inputs=stream, outputs=None, func=print_element, state=0)

x = Stream('x')
y = Stream('y')
z = Stream('z')
print_stream(x)
print_stream(y)
print_stream(z)

def h(list_of_timed_windows, threshold):
    return sum([sum([w[1] for w in timed_window])
             for timed_window in list_of_timed_windows])

tf([x,y], z, h, 10, 10, threshold=20)

x.extend([(2, 10), (6, 11), (12, 12), (14, 13), (19, 12), (22, 13), (60, 23)])
y.extend([(3, 11), (4, 15), (14, 12), (16, 13), (21, 12), (22, 13), (50, 23)])

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

def h(list_of_timed_windows, threshold):
    return sum([sum([w.value for w in timed_window])
             for timed_window in list_of_timed_windows])
# list of input streams = [x,y]
# single output stream z
tf([x,y], z, h, 10, 10, threshold=20)

x.extend([TimeAndValue(2, 10), TimeAndValue(6, 11),
          TimeAndValue(12, 12), TimeAndValue(14, 13),
          TimeAndValue(19, 12), TimeAndValue(22, 13),
          TimeAndValue(60, 23)])

y.extend([TimeAndValue(3, 11), TimeAndValue(4, 15),
          TimeAndValue(14, 12), TimeAndValue(16, 13),
          TimeAndValue(21, 12), TimeAndValue(22, 13),
          TimeAndValue(50, 23)])

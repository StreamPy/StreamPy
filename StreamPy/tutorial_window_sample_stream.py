from Stream import Stream
from Operators import wf
from examples_element_wrapper import print_stream
from random import random
""" Simple example of a windows-wrapper.

"""

x = Stream('x')
y = Stream('y')
print_stream(x)
print_stream(y)

n = 3
wf(x, y, lambda u: u[0], 1, n)

x.extend(range(20))


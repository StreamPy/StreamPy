from Stream import Stream
from Operators import stream_agent, wf
from examples_element_wrapper import print_stream
import numpy as np
from random import random
""" Simple example of a windows-wrapper.

"""

x = Stream('x')
y = Stream('y')
z = Stream('z')

print_stream(x)
print_stream(y)
print_stream(z)

stream_agent(inputs=x, outputs=y, f_type='window', f=np.mean,
             window_size=5, step_size=5)
# Alternative form
wf(x, z, np.mean, 5, 5)

x.extend([99.5+random() for _ in range(21)])

# Second example
# Illustrates that step_size may be larger than window_size.
# Stream b samples every n-th element of stream a.
a = Stream('a')
b = Stream('b')
print_stream(a)
print_stream(b)
n = 6
wf(a, b, lambda l: l[0], 1, n)
a.extend(range(18))

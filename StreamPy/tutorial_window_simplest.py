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
wf(x, z, np.mean, window_size=5, step_size=5)

x.extend([99.5+random() for _ in range(20)])

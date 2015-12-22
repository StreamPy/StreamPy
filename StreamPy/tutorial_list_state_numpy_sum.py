from Stream import Stream
from Operators import lf, stream_agent
from examples_element_wrapper import print_stream
import numpy as np

x = Stream('x')
z = Stream('z')

print_stream(x)
print_stream(z)

def cumulative(a, state):
    b = np.array(a)
    b[0] += state
    b = np.cumsum(b)
    return (b, b[-1])

lf(x, z, cumulative, 0.0)

x.extend(range(5))

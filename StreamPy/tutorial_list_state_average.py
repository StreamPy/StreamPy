from Stream import Stream
from Operators import lf, stream_agent
from examples_element_wrapper import print_stream
import numpy as np
import random

x = Stream('x')
z = Stream('z')

print_stream(x)
print_stream(z)

def average(a, state):
        n, cum = state
        b = np.array(a)
        b[0] += cum
        b = np.cumsum(b)
        n_array = np.arange(n+1, n+len(b)+1, 1)
        avg = b/np.rint(n_array)
        state = (n_array[-1], b[-1])
        return (avg, state)
# Initial state is (0, 0.0).
lf(x, z, average, (0, 0.0))

#x.extend(range(10))
x.extend([random.randint(1, 4) for _ in range(10)])

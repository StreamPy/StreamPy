from Stream import Stream
from Operators import stream_agent, ef
from examples_element_wrapper import print_stream
from source_stream import source_stream
import numpy as np
import random

"""
Example of an element-wrapper to create an agent
with multiple input streams and a single output stream.
Example functions wrapped are sum, np.mean, and (see
below) diff.

Illustrates:
      ef(x, y, sum),
      ef(x, z, np.mean), and
      ef([x[0], x[1]], w, dif).

"""

# Create streams. Call the streams of x, 'a', 'b' and 'c'.
x = [Stream('a'), Stream('b'), Stream('c')]
y = Stream('sum')
z = Stream('mean')
w = Stream('dif')

# Agents for printing
print_stream(x[0])
print_stream(x[1])
print_stream(x[2])
print_stream(y)
print_stream(z)
print_stream(w)

# Agents to make y the sum and z the mean of x
ef(x, y, sum)
ef(x, z, np.mean)

def dif(lst): return lst[1] - lst[0]
# Agent to make w x[1] - x[0]
ef([x[0], x[1]], w, dif)

# Create agents that populate the x streams with random numbers.
source_stream(output_stream=x[0], number_of_values=3, time_period=0.1,
              func=random.randint, a=0, b=100)
source_stream(output_stream=x[1], number_of_values=4, time_period=0.2,
              func=random.randint, a=0, b=10)
source_stream(output_stream=x[2], number_of_values=3, time_period=0.1,
              func=random.randint, a=0, b=20)

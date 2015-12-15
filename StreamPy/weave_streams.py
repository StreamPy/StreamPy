from Stream import Stream, _multivalue
from Operators import ef
from examples_element_wrapper import print_stream
"""Weaves a list of streams into a single stream.
Described in the tutorial.

"""

# Create streams
x=[Stream('a'), Stream('b'), Stream('c')]
y = Stream('y')

# Create printing agents
print_stream(x[0])
print_stream(x[1])
print_stream(x[2])
print_stream(y)

ef(x, y, _multivalue)

x[0].extend(range(4))
x[1].extend(range(10, 16))
x[2].extend(range(20, 25))

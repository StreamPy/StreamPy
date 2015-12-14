from Stream import Stream
from Operators import stream_agent, ef
from examples_element_wrapper import print_stream
from source_stream import source_stream
import math

def execute(v, g, h):
    return (g(v), h(v))

# Create streams
x = Stream('x')
y = Stream('y')
z = Stream('z')

# Create printing agents
print_stream(x)
print_stream(y)
print_stream(z)

# Create agent
ef(x, [y, z], execute, g=math.sqrt, h=math.exp)

# Put elements into x
x.extend(range(5))

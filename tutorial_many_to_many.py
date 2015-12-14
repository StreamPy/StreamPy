from Stream import Stream
from Operators import ef
from examples_element_wrapper import print_stream
from tutorial_split import execute
import random
"""Example illustrating multiple input stream, multiple
output streams for the tutorial.

"""

# Create streams
x = [Stream('a'), Stream('b')]
y = Stream('y')
z = Stream('z')

# Create printing agents
print_stream(x[0])
print_stream(x[1])
print_stream(y)
print_stream(z)

# Create agent
# input=x, output=[y,z], f=execute, kwargs for g,h
ef(x, [y, z], execute, g=max, h=min)

# Put elements into x
x[0].extend([random.randint(0,100) for _ in range(5)])
x[1].extend([random.randint(0,100) for _ in range(5)])

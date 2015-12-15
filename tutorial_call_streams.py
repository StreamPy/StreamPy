from Stream import Stream
from Operators import stream_agent, ef, lf
from examples_element_wrapper import print_stream
import numpy as np
""" Example of an element-wrapper with call_streams.

"""
# CREATE STREAMS AND PRINTING AGENTS
x = Stream('input')
y = Stream('sine of input')
z = Stream('clipped input')
# The two call_streams
trigger_1 = Stream('trigger_1')
trigger_2 = Stream('trigger_2')

# Create printing agents
print_stream(x)
print_stream(y)
print_stream(z)
print_stream(trigger_1)
print_stream(trigger_2)

# Create an agent that puts the sine of x into y.
# when elements appear on stream trigger_1
ef(x, y, np.sin, call_streams=[trigger_1])
# Create an agent that puts the clipped elements of x
# into z where values below a_min are set to a_min and
# values above a_max are set to a_max. This agent
# executes when elements appear in stream trigger_2.
ef(x, z, np.clip, call_streams=[trigger_2], a_min=2, a_max=8)

# Put elements 0, 1, 2, 3, 4 into stream, x.
# The agents only process elements in x when their trigger
# streams have new values.
x.extend(range(5))
# Wake up the agent that puts values into y.
trigger_1.append(1)
# Wake up the agent that puts values into z.
trigger_2.append(1)

# Put elements 5, 6, 7, 8, 9 into stream x.
x.extend(range(5, 10))
# Do NOT wake up the agent that puts values into y, but do
# wake up the agent that puts values into z.
trigger_2.append(2)

# z will have 10 elements but y will only have 5

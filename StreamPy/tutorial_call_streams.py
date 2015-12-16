from Stream import Stream
from Operators import stream_agent, ef
from examples_element_wrapper import print_stream
import numpy as np
""" Example of an element-wrapper with call_streams. The example shows
that agents with call streams wait for new values to appear on their
call streams before processing their input.

"""
# CREATE STREAMS AND PRINTING AGENTS
x = Stream('input')
y = Stream('sine of input')
z = Stream('clipped input')
# The two call_streams
# trigger_1 triggers execution of the sine agent and
# puts values into y.
# trigger_2 triggers execution of the clip agent and
# puts values into z.
trigger_1 = Stream('trigger_1')
trigger_2 = Stream('trigger_2')

# Create printing agents
print_stream(x)
print_stream(y)
print_stream(z)
print_stream(trigger_1)
print_stream(trigger_2)

# Create an agent that puts the sine of x into y.
# when elements appear on stream trigger_1. This
# agent remains asleep until woken up by new elements
# in trigger_1.
ef(x, y, np.sin, call_streams=[trigger_1])
# Create an agent that puts the clipped elements of x
# into z where values below a_min are set to a_min and
# values above a_max are set to a_max. This agent
# executes when elements appear in stream trigger_2.
# This agent remains asleep until woken up by new elements
# in trigger_2.
ef(x, z, np.clip, call_streams=[trigger_2], a_min=2, a_max=8)

# Put elements 0, 1, 2, 3, 4 into stream, x.
# The agents only process elements in x when their trigger
# streams have new values.
x.extend(range(5))
# Wake up the agent that puts values into y.
# Now y has 5 values: sine(0),... , sine(4)
trigger_1.append(1)
# Wake up the agent that puts values into z.
# Now z has 5 values: clip(0, 2, 8).... clip(4, 2, 8)
trigger_2.append(1)

# Put elements 5, 6, 7, 8, 9 into stream x.
x.extend(range(5, 10))
# Now x has 10 values 0, ..., 9 whereas y and z each
# have 5 values.
# Do NOT wake up the agent that puts values into y, but do
# wake up the agent that puts values into z.
trigger_2.append(2)
# Now z has 10 values: clip(0, 2, 8).... clip(9, 2, 8)
# because the clip agents was woken up by trigger 2, and
# the agent processed the messages 5, ..., 9 waiting for it
# and it put 5 values into z.
# y only has 5 values: sine(0),... , sine(4) because the
# sine agent was not woken up, because no additional message
# was put into trigger_1.

# In summary: now z has 10 elements but y has only 5.

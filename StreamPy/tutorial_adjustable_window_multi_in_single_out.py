from Stream import Stream
from Operators import stream_agent, adjustable_window_agent, awf
from examples_element_wrapper import print_stream
import numpy as np
from random import randint
"""Example of awf, adjustable window function, with state.
The output is the maximum over all the input streams of
the standard deviation of the window into the input stream.
If the next output is greater than the last output
then the window size and step size are increased;
otherwise the window size and step size are decreased
if greater than 4.

NOTE: step size must be non_zero and must eventually
be positive. A negative step size implies that the
agent reads elements of the stream that it had earlier
determined it would no longer need. If the step size
remains zero for ever then the agent will always need
to access the entire stream, even as the stream length
gets arbitrarily large.

"""
# Create streams and printing agents
u = Stream('u')
v = Stream('v')
y = Stream('y')
#print_stream(u)
#print_stream(v)
print_stream(y)

# Function used by awf
def h(list_of_windows, window_size, step_size, last_output,
      percent_increase, min_window_size):
    next_output =  max([np.std(window) for window in list_of_windows])
    if next_output > (1 + percent_increase/100.0) * last_output:
        window_size += 1
        step_size += 1
    elif window_size > min_window_size:
        window_size -= 1
        step_size -= 1
    print 'window_size', window_size
    # return output, next window size, next step size, next state
    return (next_output, window_size, step_size, next_output)

initial_window_size = 5
initial_step_size = 5
last_output = 0

# Input streams: u, v
# Output stream: y
# Function: h
# state is last_output
# Create agent
awf([u,v], y, h, initial_window_size, initial_step_size, last_output,
    percent_increase=5.0, min_window_size=4)

# Put data into the input streams.
u.extend([randint(0, 20) for _ in range(60)])
v.extend([randint(0, 20) for _ in range(60)])

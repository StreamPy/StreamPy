from Stream import Stream
from Operators import stream_agent, adjustable_window_agent, awf
from examples_element_wrapper import print_stream
import numpy as np
from random import randint
""".Example illustrating continuously adjustable windows
using awf: adjustable window function.
Parameters of awf are:
  inputs, outputs, func, window_size, step_size,
  state=None, call_streams=None, **kwargs
The parameters of func are:
  list or list of lists, window_size, step_size
and func returns:
  output or list of outputs, new window_size, new step_size.

In this example, func is h. The first parameter of h is
lst, a single list. This is because awf creates an agent with
a single input.
h returns a tuple: sum(lst) which is the next element of the
output stream and the new window and step sizes.
In this example, h has no state or call streams.

awf(x, y, h, initial_window_size, initial_step_size) creates
an agent with input stream x, output stream y, func h, and
with the specified initial window and step sizes.

"""

x = Stream('x')
y = Stream('y')
print_stream(x)
print_stream(y)

def h(window, window_size, step_size, threshold):
    if sum(window) > threshold:
        window_size -= 1
        step_size -= 1
    else:
        window_size += 1
        step_size += 1
    # print output to help understand the program.
    print 'sum(window) =', sum(window), 'window_size =', window_size
    return (sum(window), window_size, step_size)

initial_window_size = 5
initial_step_size = 5
awf(x, y, h, initial_window_size, initial_step_size, threshold=40)
# Put data into the input stream.
x.extend([randint(0, 20) for _ in range(20)])


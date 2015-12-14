from Stream import Stream, _multivalue
from Operators import ef
from examples_element_wrapper import print_stream
import numpy as np

"""Example of element wrapper with state and keyword
arguments for tutorial.

"""

def update_smooth(lst, state, h, alpha):
    state = state*(1-alpha) + h(lst)*alpha
    return (state, state)

# Create streams
x = [Stream('a'), Stream('b'), Stream('c')]
y = Stream('y')

# Create printing agents
print_stream(x[0])
print_stream(x[1])
print_stream(x[2])
print_stream(y)

init = 100
ef(x, y, update_smooth, init, h=np.mean, alpha=0.5)

x[0].extend(range(10))
x[1].extend(range(100, 110))
x[2].extend(range(200, 210))

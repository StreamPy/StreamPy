from Stream import Stream, _multivalue, StreamArray
from Operators import wf
from examples_element_wrapper import print_stream
import numpy as np

x = StreamArray('x')
y = StreamArray('y')
print_stream(x)
print_stream(y)
num_windows = 3

def h(a, state):
    state = np.roll(state, -1, axis=1)
    state[:, -1] = [a.sum(), len(a)]
    return (_multivalue
            (a - state[0,:].sum()/float(state[1,:].sum())), state)

initial_state = np.zeros([2, num_windows])
wf(x, y, h, 4, 4, initial_state)

x.extend(np.arange(24))

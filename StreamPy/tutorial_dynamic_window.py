from Stream import Stream
from Operators import stream_agent, wf, dynamic_window_func
from examples_element_wrapper import print_stream
import numpy as np
from random import randint
""".

"""

x = Stream('x')
print_stream(x)


def h(lst, state):
    print 'lst', lst
    if sum(lst) > 60:
        reset = True
        state[2] = reset
    return (sum(lst), state)

initial_window_size = 4
steady_state = False
reset = False
initial_state = [initial_window_size, steady_state, reset]

y = dynamic_window_func(
    f=h,
    inputs=x,
    state=initial_state,
    min_window_size=2,
    max_window_size=8,
    step_size=1)
y.set_name('y')

print_stream(y)

#x.extend([randint(0, 20) for _ in range(20)])
x.extend(range(20))

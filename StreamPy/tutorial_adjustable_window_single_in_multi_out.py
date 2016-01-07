from Stream import Stream
from Operators import adjustable_window_agent, awf
from examples_element_wrapper import print_stream
import numpy as np
from random import randint
""".

"""

w = Stream('w')
x = Stream('x')
y = Stream('y')
z = Stream('z')
print_stream(x)
print_stream(y)
print_stream(z)

def h(window, window_size, step_size, threshold, min_window_size):
    mx = max(window)
    mn =  min(window)
    dif = mx - mn
    if dif < threshold:
        window_size += 1
        step_size += 1
    elif window_size > min_window_size:
        window_size -= 1
        step_size -= 1

    # print to help understand the program
    print 'dif = ', dif, 'window_size = ', window_size

    return ([mx, mn, dif], window_size, step_size)

initial_window_size = 6
initial_step_size = 6

awf(w, [x,y,z], h, initial_window_size, initial_step_size,
    threshold=15, min_window_size=1)

w.extend([randint(0, 20) for _ in range(60)])

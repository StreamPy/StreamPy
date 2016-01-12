from Stream import Stream, TimeAndValue
from Operators import stream_agent, timed_agent, tf
from examples_element_wrapper import print_stream

x = Stream('x')
print_stream(x)
y = Stream('y')
print_stream(y)

def h(window):
    print 'window', window
    return sum(v[1] for v in window)

tf(inputs=x, outputs=y, func=h, window_size=10, step_size=10)

x.extend([(2, 10), (6, 11), (12, 12), (14, 13), (19, 12), (32, 13)])

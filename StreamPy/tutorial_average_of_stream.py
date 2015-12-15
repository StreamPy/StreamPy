from Stream import Stream, _multivalue
from Operators import ef
from examples_element_wrapper import print_stream

def update_avg(v, state):
    state[0] +=1
    state[1] += v
    return (state[1]/float(state[0]), state)

# Create streams
x = Stream('x')
y = Stream('y')

# Create printing agents
print_stream(x)
print_stream(y)

# Create the agent that puts averages of x into y.
ef(x, y, update_avg, [0, 0.0])

# Put elements into x
x.extend(range(10))

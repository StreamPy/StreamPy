from Stream import Stream
from Operators import stream_agent, lf
from examples_element_wrapper import print_stream
from random import randint

# Returns even numbers in list xdef evens(x):
    return [v for v in x if v%2 == 0]

# Returns multiplier times elements in list x
def multiply(x, multiplier):
    return [v*multiplier for v in x]

w = Stream('w')
x = Stream('x')
y = Stream('y')
z = Stream('z')
print_stream(w)
print_stream(x)
print_stream(y)
print_stream(z)

def double_list(lst): return [2*element for element in lst]
stream_agent(inputs=x, outputs=z, f_type='list', f=double_list)

# Using lf rather than stream_agent
# y consists of even numbers in stream x
lf(x, y, evens)
# z consists of multiplier times elements in list x
lf(x, w, multiply, multiplier=3)

x.extend([randint(0, 5) for _ in range(4)])

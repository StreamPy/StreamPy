from Stream import Stream
from Operators import lf
from examples_element_wrapper import print_stream
from random import randint

"""Example illustrating single input stream, multiple
output streams for the tutorial. This example also
illustrate lf (list function) and kwargs.

"""
# Function that is encapsulated
def split_on_func(x, bool_func):
    y = list()
    z = list()
    for v in x:
        if bool_func(v):
            y.append(v)
        else:
            z.append(v)
    return (y, z)

# Function used as parameter bool_func
def g(v):
    return v > 5
    
# Create streams
x = Stream('x')
y = Stream('y')
z = Stream('z')
# Create printing agents
print_stream(x)
print_stream(y)
print_stream(z)

# Create agent using lf: list function
# single input stream: x, Output streams: y, z
# f = split_on_func, kwargs: {bool_func:g}
lf(x, [y, z], split_on_func, bool_func=g)

# Put random numbers into stream x to
# drive the computation.
x.extend([randint(0, 10) for _ in range(10)])

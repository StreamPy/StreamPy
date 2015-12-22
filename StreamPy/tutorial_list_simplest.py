from Stream import Stream
from Operators import lf
from examples_element_wrapper import print_stream
from random import randint

def evens(x):
    return [v for v in x if v%2 == 0]

def multiply(x, multiplier):
    return [v*multiplier for v in x]

x = Stream('x')
y = Stream('y')
z = Stream('z')
print_stream(x)
print_stream(y)
print_stream(z)

lf(x, y, evens)
lf(x, z, multiply, multiplier=3)

x.extend([randint(0, 4) for _ in range(4)])

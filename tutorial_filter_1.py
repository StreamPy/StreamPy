from Stream import Stream, _no_value
from Operators import ef
from examples_element_wrapper import print_stream
""" Example that illustrates the element wrapper with _no_value.


"""

# Create streams
x = Stream('x')
y = Stream('y')

# Create printing agents
print_stream(x)
print_stream(y)

def ft(v, threshold):
    return v if v > threshold else _no_value

# Create agent
ef(x, y, ft, threshold=5)

# Put values into x
x.extend(range(10))

from Stream import Stream
from Operators import lf, stream_agent
from examples_element_wrapper import print_stream

def h(u):
    return [2*v[0]+v[1] for v in zip(*u)]

x = Stream('x')
y = Stream('y')
z = Stream('z')
print_stream(x)
print_stream(y)
print_stream(z)

lf([x,y], z, h)

x.extend(range(100, 104))
y.extend(range(5))

x.extend(range(200, 204))
y.extend(range(10, 15))

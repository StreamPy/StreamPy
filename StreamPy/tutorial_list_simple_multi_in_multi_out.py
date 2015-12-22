from Stream import Stream
from Operators import lf, stream_agent
from examples_element_wrapper import print_stream

def h(x, weights, threshold):
    lst = [sum([weights[i]*v[i]
                for i in range(min(len(weights), len(x)))])
           for v in zip(*x)]
    above = [v for v in lst if v > threshold]
    below = [v for v in lst if v <= threshold]
    return (above, below)

u = Stream('u')
v = Stream('v')
w = Stream('w')
a = Stream('a')
b = Stream('b')

print_stream(u)
print_stream(v)
print_stream(w)
print_stream(a)
print_stream(b)

lf([u,v,w], [a,b], h, weights=(2,5,1), threshold=40)

u.extend(range(10,15))
v.extend(range(4))
w.extend(range(20, 25))

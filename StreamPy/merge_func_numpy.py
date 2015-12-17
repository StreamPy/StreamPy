from Stream import Stream
from Operators import stream_agent, lf
from examples_element_wrapper import print_stream
import numpy as np
import random
"""Example illustrating the list wrapper with multiple
input streams and a single output stream with the use
of NumPy array reduction operations such as sum, mean,
variance, standard deviation, all, any.

output[j] = func(x[j], y[j], z[j])
where func is the reduction operation.

"""

# Create streams
u = Stream('u')
v = Stream('v')
w = Stream('w')
a = Stream('sum')
b = Stream('mean')
c = Stream('variance')
d = Stream('all')
x = [ u, v, w]

# Create printing agents
print_stream(u)
print_stream(v)
print_stream(w)
print_stream(a)
print_stream(b)
print_stream(c)
print_stream(d)
# Create agents to put values into a,b,c,d
lf(x, a, np.sum, axis=0)
lf(x, b, np.mean, axis=0)
lf(x, c, np.var, axis=0)
lf(x, d, np.all, axis=0)

# Put elements into x
u.extend([random.randint(0,10) for _ in range(5)])
v.extend([random.randint(0,10) for _ in range(5)])
w.extend([random.randint(0,10) for _ in range(5)])




    

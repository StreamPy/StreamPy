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
x = Stream('x')
y = Stream('y')
z = Stream('z')
a = Stream('sum')
b = Stream('mean')
c = Stream('variance')
d = Stream('all')

# Create printing agents
print_stream(x)
print_stream(y)
print_stream(z)
print_stream(a)
print_stream(b)
print_stream(c)
print_stream(d)

# Put elements into x
x.extend([random.randint(0,10) for _ in range(5)])
y.extend([random.randint(0,10) for _ in range(5)])
z.extend([random.randint(0,10) for _ in range(5)])

def execute_list_of_np_func(v, list_of_np_func):
    return ([f(v, axis=0) for f in list_of_np_func])

lf([x,y,z], [a,b,c,d], execute_list_of_np_func,
   list_of_np_func=[np.sum, np.mean, np.var, np.all])




    

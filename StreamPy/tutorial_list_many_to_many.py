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

def merge_func(list_of_input_streams, output_stream, func):
    def f(list_of_lists):
        return func(np.array(list_of_lists), axis=0)
    ## stream_agent(
    ##     inputs=list_of_input_streams, outputs=output_stream,
    ##     f_type ='list', f=f)
    lf(list_of_input_streams, output_stream, f)
       

merge_func([x, y, z], a, np.sum)
merge_func([x, y, z], b, np.mean)
merge_func([x, y, z], c, np.var)
merge_func([x, y, z], d, np.all)

# Put elements into x
x.extend([random.randint(0,10) for _ in range(5)])
y.extend([random.randint(0,10) for _ in range(5)])
z.extend([random.randint(0,10) for _ in range(5)])

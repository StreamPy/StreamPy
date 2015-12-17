from Stream import Stream
from Operators import lf, stream_agent
from examples_element_wrapper import print_stream
import numpy as np
"""This example illustrates the use of the same NumPy
operations on single elements and on lists.

Observe that the elements of streams y and z are the
same for the first n (n=12) elements, and that stream
y eventually has m (m=24) elements whereas z only has n
elements. This is because the y-agent (i.e., the agent
that puts values into y) is triggered after m elements
are inserted into x whereas the z-agent is triggered only
after n elements are inserted into x. This computation
terminates with a backlog of unprocessed data for the
z-agent.

"""
# Create streams
x = Stream('x')
y = Stream('y')
z = Stream('z')
trigger_1 = Stream('trigger_1')
trigger_2 = Stream('trigger_2')
# Create printing agents
print_stream(x)
print_stream(y)
print_stream(z)

# Create list-wrapper agent triggered by trigger_1
stream_agent(x, y, 'list', np.sin, call_streams=[trigger_1])
# Create element_wrapper agent triggered by trigger_2
stream_agent(x, z, 'element', np.sin, call_streams=[trigger_2])

n = 12
m = 2*n
x.extend([np.pi*j/float(m) for j in range(n)])
# At his point, x has n elements, and y and z have
# no elements because no values have yet been appended
# to trigger_1 or trigger_2.
trigger_2.append(1)
# At this point z also has n elements because the z-agent
# was woken up by a message in trigger_2 after x had n
# elements.
# At this point y has no elements because the y-agent
# has not been woken up yet because no messages were
# added to trigger_1.

x.extend([np.pi*j/float(m) for j in range(n, m)])
# At this point, x has m (m=2n) elements.
trigger_1.append(2)
# The number of elements in z has not changed because
# no new value was appended to trigger_2.
# The number of elements in y is now m because the
# y-agent was woken up after x had m elements.

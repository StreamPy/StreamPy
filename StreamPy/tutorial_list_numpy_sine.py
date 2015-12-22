from Stream import Stream
from Operators import stream_agent, lf
from examples_element_wrapper import print_stream
import numpy as np
""" Example of a list-wrapper to create an agent
with a single input stream and a single output stream.
The function that is wrapped is np.sin.

Illustrates: lf(x, y, np.sin)

"""
# CREATE STREAMS AND PRINTING AGENTS
# Create a stream x and call it 'input'
x = Stream('input')
# Create a stream y and call it 'sine of input'
y = Stream('sine of input')
# Create an agent that prints stream x
print_stream(x)
# Create an agent that prints stream y
print_stream(y)

# Create an agent that puts the sine of x into y.
lf(x, y, np.sin)

# ALTERNATIVE WAY OF SPECIFYING THE AGENT
#stream_agent(inputs=x, outputs=y, f_type='list', f=np.sin)

# Put elements into the input stream, x.
# As elements enter x, an agent will put elements into y, and
# the printer agents will print elements from x and y.
for _ in range(2):
    x.extend(np.linspace(0, np.pi, 8))

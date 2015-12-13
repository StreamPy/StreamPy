from Stream import Stream
from Operators import stream_agent
from examples_element_wrapper import print_stream
import numpy as np
""" Example of an element-wrapper to create an agent
with a single input stream and a single output stream.
The function that is wrapped is np.sin.
"""

# Create a stream input_stream and call it 'input'
input_stream = Stream('input')
# Create a stream output_stream and call it 'sine of input'
output_stream = Stream('sine of input')
# Create an agent that prints stream input_stream.
print_stream(input_stream)
# Create an agent that prints stream output_stream
print_stream(output_stream)
# Create an agent that puts the sine of elements of
# input_stream into output_stream by wrapping np.sin
# using the element wrapper.
stream_agent(inputs=input_stream, outputs=output_stream,
             f_type='element', f=np.sin)

# Put numbers into input_stream. 
for _ in range(2):
    input_stream.extend(np.linspace(0, np.pi, 8))

# As elements are placed in the input stream, the agent that we
# created using the wrapper will put elements into
# output_stream.
# Also each printing agent will print elements from its stream as
# elements enter the stream.
# Note that multiple agents will be printing simultaneously
# and so the print lines may be interspersed.

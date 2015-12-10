from Stream import Stream
from Operators import stream_agent
from examples_element_wrapper import print_stream
import numpy as np
""" Example of an element-wrapper to create an agent
with a single input stream and a single output stream.
The function that is wrapped is np.sin.
"""

# Create a stream x and call it 'input'
input_stream = Stream('input')
# Create a stream y and call it 'sine of input'
output_stream = Stream('sine of input')
# Create an agent that prints stream input_stream.
# This agent will print elements that enter input_stream.
print_stream(input_stream)
# Create an agent that prints stream output_stream.
print_stream(output_stream)
# Create an agent that puts the sine of elements of
# input_stream into output_stream. This agent is created by
# wrapping np.sin using the element wrapper.
# As elements are added to input_stream, this agent will put
# sine of these elements in output_stream.
stream_agent(inputs=input_stream, outputs=output_stream,
             f_type='element', f=np.sin)

# Put numbers into the input stream to drive all
# the other agents.
for _ in range(2):
    input_stream.extend(np.linspace(0, np.pi, 8))

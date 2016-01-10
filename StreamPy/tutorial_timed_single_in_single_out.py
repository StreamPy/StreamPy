from Stream import Stream, TimeAndValue
from Operators import stream_agent, timed_agent, tf
from examples_element_wrapper import print_stream

x = Stream('x')
print_stream(x)
y = Stream('y')
print_stream(y)

def h(window):
    print 'window', window
    return [sum(t_and_v.value for t_and_v in window)]

## timed_agent(f=h, inputs=[x], outputs=[y], state=None, call_streams=None,
##                window_size=10, step_size=10)

## stream_agent(inputs=x, outputs=y, f_type ='timed', f=h,
##             state=None, call_streams=None,
##             window_size=10, step_size=10)

tf(inputs=x, outputs=y, func=h, window_size=10, step_size=10)

x.extend([TimeAndValue(2, 10), TimeAndValue(6, 11),
          TimeAndValue(12, 12), TimeAndValue(14, 13),
          TimeAndValue(19, 12), TimeAndValue(22, 13)])

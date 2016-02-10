from Stream import Stream, _multivalue, StreamArray
from Operators import wf
from examples_element_wrapper import print_stream
import numpy as np

def demean_across_multiple_windows(window, state):
        state = np.roll(state, -1, axis=1)
        state[:, -1] = [window.sum(), len(window)]
        output = _multivalue(
            window - state[0,:].sum()/float(state[1,:].sum()))
        return (output, state)

def demean_stream(in_stream, window_size, step_size,
                  num_windows, initial_state=None):
    out_stream = StreamArray()
    if initial_state is None:
        initial_state=np.zeros([2, num_windows])
    wf(in_stream, out_stream, demean_across_multiple_windows,
       window_size, step_size, initial_state)
    return out_stream


def main():
    in_stream=StreamArray('in_stream')
    out_stream = demean_stream(
        in_stream=in_stream,
        window_size=4,
        step_size=4,
        num_windows=3)
        
    out_stream.name = 'demeaned stream'
    print_stream(in_stream)
    print_stream(out_stream)

    in_stream.extend(np.arange(24))
    return

if __name__ == '__main__':
    main()

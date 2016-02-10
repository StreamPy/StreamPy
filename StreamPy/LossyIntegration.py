import numpy as np
from Stream import StreamArray, _multivalue
from Operators import wf
from examples_element_wrapper import print_stream
import numpy as np

def lossy_integration(data, initial_value, FACTOR):
    data[0] -= initial_value * FACTOR
    for i in range(1, np.shape(data)[0]):
        data[i] -= data[i-1]*FACTOR
    return (_multivalue(data), data[-1])

def lossy_integrate_stream(
        in_stream, window_size, initial_value, FACTOR):
    out_stream = StreamArray()
    wf(in_stream, out_stream, lossy_integration,
       window_size, window_size, initial_value, FACTOR=FACTOR)
    return out_stream


def main():
    """For input:
          data=[2, 5, 8, 11, 14, 17, ...],
          initial_value=2,
       the expected output is:
          [ 2  4  6  8 10 12 ....]

    """
    print lossy_integration(
        data=np.array([2, 5, 8, 11, 14, 17]),
        initial_value=0,
        FACTOR=0.5)

    in_stream = StreamArray('in_stream')
    out_stream = lossy_integrate_stream(
        in_stream, window_size=4, initial_value=0.0, FACTOR=0.5)
    out_stream.name = "integrated"
    print_stream(in_stream)
    print_stream(out_stream)
    in_stream.extend([2+3*i for i in range(12)])

if __name__ == '__main__':
    main()
    


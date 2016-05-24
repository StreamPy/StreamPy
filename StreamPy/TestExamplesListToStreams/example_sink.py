if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Stream import Stream, _no_value
from Operators import stream_func
import numpy as np

def main():

    def print_stream(stream):

        def print_list(lst):
            for v in lst:
                print 'from print_list {0} : {1}'.format(stream.name, v)

        return stream_func(
            inputs=stream, f_type='list',
            f=print_list, num_outputs=0)

    def print_stream_elements(stream):

        def print_element(v):
            print 'from print_element {0} : {1}'.format(stream.name, v)

        return stream_func(
            inputs=stream,
            f_type='element',
            f=print_element,
            num_outputs=0)

    def average(v, state):
        """ This function is used to output a stream
        where the n-th value on the output stream is
        the average of the first n values of the
        input stream.
        
        The state of the input stream is the pair (n,cum).
        When used to create a stream, n is the number
        of values received on the input stream, and cum
        is the sum of all the values in the input stream
        received so far.
        v is the next value received in the input stream.
        
        """
        n, cum = state
        n += 1
        print 'cum, v', cum, v
        cum += v
        mean = cum/float(n)
        state = (n, cum)
        print 'avg up to this point is', mean
        return (None, state)

    def average_stream(stream):
        return stream_func(
            inputs=stream,
            f_type='element',
            f=average,
            num_outputs=0,
            state=(0,0.0)
            )
        

    x = Stream('x')
    print_stream(x)

    ## y = Stream('y')
    ## z=print_stream_elements(y)

    ## a = average_stream(x)

    x.extend([1, 2])
    x.print_recent()
    x.extend([0, 1, 3])
    x.print_recent()

if __name__ == '__main__':
    main()

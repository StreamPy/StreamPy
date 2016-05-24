"""This module contains examples of stream_func where f_type
is 'element' and stream_func has a list of multiple input streams,
a single output stream, and the operation is stateless. These
examples must have a LIST of input streams and not a single
input stream.

The functions on static Python data structures are of the form:
    list -> element

"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Stream import Stream, _no_value
from Operators import stream_func


def main():
    # Functions: list, state -> list, state
    delta = 0.5 
    def inrange_and_outlier(x_and_y, state):
        # Each point (x,y) is used to build a
        # linear regression model and then the
        # values of y are compared against the
        # predictions of the model for y.
        x, y = x_and_y
        # parameters of the regression model
        a, b, n, x_sum, y_sum, xx_sum, xy_sum = state
        # Compute output.
        # Check if (x,y) falls outside the model.
        # The model is specified by a, b.
        if abs(a*x + b - y) > delta*abs(y):
            # (x,y) is an outlier.
            # The streams returned by stream func are:
            # [inrange stream, outlier stream]
            # Return _no_value for the inrange stream
            # because this point is not in range.
            return_list = [_no_value, x_and_y]
        else:
            # (x,y) is inrange.
            # Return _no_value for the outlier stream.
            return_list = [x_and_y, _no_value]

        # Update the regression parameters by
        # updating the next state
        n += 1
        x_sum += x
        y_sum += y
        xy_sum += x*y
        xx_sum += x*x
        a = (xy_sum - x_sum*y_sum/float(n))/(xx_sum - x_sum*x_sum/float(n))
        b = y_sum/float(n) - a*x_sum/float(n)
        state = a, b, n, x_sum, y_sum, xx_sum, xy_sum
        return (return_list, state)


    # Functions: stream -> stream.
    # The n-th element of the output stream is f() applied to the n-th
    # elements of each of the input streams.
    # Function mean is defined above, and functions sum and max are the
    # standard Python functions.
    # state = a, b, n, x_sum, y_sum, xx_sum, xy_sum
    # xx_sum is set to a small value to avoid division by 0.0
    # n is set to 2 to reflect that the regression is assumed to have
    # been running for at least 2 points.
    state=(1.0, 0.0, 2, 0.0, 0.0, 0.001, 0.0)
    inrange_and_outlier_streams = partial(stream_func, f_type='element',
                                         f=inrange_and_outlier,
                                         num_outputs=2, state=state)

    # Create stream x, and give it name 'x'.
    x = Stream('input_0')
    y = Stream('input_1')

    
    inrange_stream, outlier_stream = inrange_and_outlier_streams([x,y])

    # Give names to streams u, v, and w. This is helpful in reading output.
    inrange_stream.set_name('inrange')
    outlier_stream.set_name('outlier')

    print
    # Add values to the tail of stream x.
    x.extend(range(10, 15, 1))
    y.extend(range(10, 15, 1))

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()

    print 'recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    print
    print 'Adding [15, 16, ...19], [150, 160,..190] to 2 streams.'
    # Add more values to the tail of stream x.
    x_list = range(15, 20, 1)
    y_list = [10*v for v in x_list]
    
    x.extend(x_list)
    y.extend(y_list)

    # Print recent values of the streams
    print 'recent values of input streams'
    x.print_recent()
    y.print_recent()

    print 'recent values of output streams'
    inrange_stream.print_recent()
    outlier_stream.print_recent()

    print
    print 'The regression parameters take some time to adjust'
    print 'to the new slope. Initially x = y, then x = 10*y'


if __name__ == '__main__':
    main()


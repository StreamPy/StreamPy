if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from functools import partial
from Stream import Stream, _no_value, _multivalue

from Operators import stream_func
import numpy as np

from stream_test import *


# EXAMPLE FUNCTIONS ON WINDOWS
# Functions have a single input: a list
# which is the list of values in a window.
# Functions return a scalar value, _no_value
# or a list, _multivalue().

window_size = 2
step_size = 2
print "examples of window operation"    
print "window_size = ", window_size
print "step_size = ", step_size
print ""

# function that operates on a window, i.e., a list
# and that returns a scalar value, _no_value
# or a list, _multivalue().
def example_of_no_value(lst):
    v = sum(lst)
    if not v%2:
        # v is even.
        # The output stream should have
        # two elements, v/2 and v, for
        # this single value of v.
        return _multivalue([v/2, v])
    else:
        # v is odd
        # The output stream should not have
        # any value for this v.
        return _no_value

# EXAMPLE STREAM FUNCTION
# Wrapper for the list function to get a stream function
# This example shows the use of Python's 'partial' feature
# in the wrapper.
# The next example shows how to specify a wrapper
# using the definition of a stream function.
window_sum = partial(stream_func, f_type='window',
                     f=sum, num_outputs=1,
                     window_size=2, step_size=2)


# EXAMPLE STREAM FUNCTION
# Wrapper for the list function to get a stream function.
# This example shows the specification of a wrapper
# using a definition of a function on streams whereas
# the previous example showed a wrapper using 'partial'.
def window_example_of_novalue(stream):
    return stream_func(inputs=stream,
                       f_type='window',
                       f=example_of_no_value,
                       num_outputs=1,
                       window_size=2,
                       step_size=2)


# EXAMPLE STREAM FUNCTION
def ksigma_of_stream(
        input_stream, base_period_length, gap_length,
        sigma_threshold):
    window_size = base_period_length+gap_length+1

    # function that operates on a window, i.e., a list
    # and that returns a scalar value
    def ksigma_calculation(lst):
        # lst is the window
        # The window consists of a base period, followed by
        # a gap, followed by the current period. The
        # current period consists of a single value.
        base_period = lst[:base_period_length]            
        base_standard_deviation = np.std(lst[:base_period_length])
        base_mean = np.mean(lst[:base_period_length])
        current_period_value = lst[-1]
        if current_period_value > base_mean and base_standard_deviation > 0.0:
            ksigma = ((current_period_value - base_mean) /
                      base_standard_deviation)
        else:
            ksigma = 0.0

        ## # debugging output
        ## print 'base_period = ', lst[:base_period_length]
        ## print 'base_mean = ', base_mean
        ## print 'base standard deviation = ', base_standard_deviation
        ## print 'current period value =', current_period_value
        ## print 'ksigma = ', ksigma

        return ksigma

    # Wrapper for the list function to get a stream function.
    return stream_func(
        inputs=input_stream,
        f_type='window',
        f=ksigma_calculation,
        num_outputs=1,
        window_size=window_size,
        step_size=1)


def test():


    # STREAMS TO DRIVE THE EXAMPLES
    x = Stream('input stream')
    # x is the in_stream.
    # sum() is the function on the window

    # Example illustrating the use of the wrapper
    # to generate the mean values of windows into
    # stream x.
    z = stream_func(x, f_type='window', f=np.mean,
                    num_outputs=1,  window_size=2,
                    step_size=2)

    # Examples illustrating the use of predefined
    # stream functions, window_sum and
    # window_example_of_novalue.
    y = window_sum(x)
    a = window_example_of_novalue(x)

    # Set stream names to help in reading printed
    # output
    y.set_name('sum window')
    z.set_name('average window')
    a.set_name('_no_value example')

    check(y, [17, 24, 27, 39, 21])
    check(z, [8.5, 12.0, 13.5, 19.5, 10.5])
    check(a, [12, 24])
 

    x.extend([6, 11])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    a.print_recent()
    print

    x.extend([9, 15, 19, 8, 20])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    a.print_recent()
    print
    
    x.extend([19, 10, 11, 28, 30])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    a.print_recent()
    print

    ks_input_stream = Stream('ks_input')
    ks = ksigma_of_stream(
        input_stream=ks_input_stream,
        base_period_length=4,
        gap_length=2,
        sigma_threshold=1)
    ks.set_name('ksigma output stream')

    check(ks, [64.510464267434884, 67.105247825444167, 1.6639140198552489, 0.97061623337301206])

    ks_input_stream.extend([1.01, 1.02, 0.99, 0.98, 1.0, 2.01, 2.02, 1.99, 1.98, 2.0, 1.01])
    ks_input_stream.print_recent()
    ks.print_recent()

    check_empty()
    

if __name__ == '__main__':
    test()

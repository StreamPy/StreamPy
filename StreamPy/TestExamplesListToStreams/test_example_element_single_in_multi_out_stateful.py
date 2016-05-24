"""This module contains examples of stream_func where f_type
is 'element' and stream_func has a list of multiple input streams,
a single output stream, and the operation is stateless. These
examples must have a LIST of input streams and not a single
input stream.

The functions on static Python data structures are of the form:
    list -> element

"""
if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Stream import Stream, _no_value
from Operators import stream_func

from stream_test import *


# Functions: element,state -> list,state
def split_by_sensor_id(sensor_id_value_tuple, state):
    """ This function is a single step in the computation
    of the average of values received so far for each id
    in the input stream.

    Parameters
    ----------
    sensor_id_value_tuple: A tuple (id, value)
                    id is 0 or 1
                    value is a number.
    state: tuple (number_list, sum_list)
                    number_list is a list of two elements
                    where number_list[k[ is the number of
                    tuples received on the input stream with
                    id k.
                    sum_list is a list of two elements
                    where sum_list[k] is the sum of the values
                    received on the input stream for which
                    the corresponding value is k.
                    
    Returns: (return_list, state)
    -------
              return_list[k] is _no_value if id is not k.
              This is because if the id is not k then the output
              stream for id k is not modified.
              return_list[k] is the average of all the numbers
              received so far if id is k.
    """
    number_list, sum_list = state
    sensor_id, sensor_value = sensor_id_value_tuple
    number_list[sensor_id] += 1
    sum_list[sensor_id] += sensor_value
    state = (number_list, sum_list)
    average = sum_list[sensor_id]/float(number_list[sensor_id])
    return_list = [_no_value, _no_value]
    return_list[sensor_id] = average
    return (return_list, state)

# Functions: stream -> stream.
# The n-th element of the output stream is f() applied to the n-th
# elements of each of the input streams.
# Function mean is defined above, and functions sum and max are the
# standard Python functions.

# Initially, the number of values received for each id is 0
# and the sum of values received for each id is 0.0
state=([0, 0], [0.0, 0.0])
stream_split_by_sensor_id = \
  partial(stream_func, f_type='element', f=split_by_sensor_id,
          num_outputs=2, state=state)


def test():

    # Create stream x, and give it name 'x'.
    x = Stream('input_0')

    id_0_average, id_1_average = stream_split_by_sensor_id(x)

    # Give names to streams u, v, and w. This is helpful in reading output.
    id_0_average.set_name('average of id_0 sensors in x')
    id_1_average.set_name('average of id_1 sensors in x')

    check(id_0_average, [2.0, 3.0, 5.0, 4.0, 4.0])
    check(id_1_average, [5.0, 3.0, 3.0, 4.0, 5.0, 6.0])

    print
    print 'Adding ([(0,2), (0,4), (1,5), (1,1), (0,9)]'
    print 'to the input stream.'
    # Add values to the tail of stream x.
    x.extend([(0,2), (0,4), (1,5), (1,1), (0,9)])

    # Print recent values of the streams
    print
    print 'recent values of input streams'
    x.print_recent()

    print
    print 'recent values of output streams'
    id_0_average.print_recent()
    id_1_average.print_recent()

    print
    print
    print 'Adding ([(1,3), (1,7), (0,1), (1,9), (1,11), (0,4)])'
    print 'to the input stream.'
    # Add values to the tail of stream x.
    x.extend([(1,3), (1,7), (0,1), (1,9), (1,11), (0,4)])

    # Print recent values of the streams
    print 'recent values of input streams'
    print
    x.print_recent()

    print 'recent values of output streams'
    print
    id_0_average.print_recent()
    id_1_average.print_recent()

    check_empty()

if __name__ == '__main__':
    test()


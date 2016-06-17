"""This module contains examples of the stateless single stream source
"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from ListOperators import stream_func

# Stream function
def average_by_sensor_type_stream(input_stream):
    # List function: list, state -> list of lists, state
    def average_by_sensor_type_list(input_list, state):
        number_type_0, number_type_1, sum_type_0, sum_type_1 = state
        averages_list_type_0 = list()
        averages_list_type_1 = list()
        for (type, value) in input_list:
            if type == 1:
                number_type_1 += 1
                sum_type_1 += value
                averages_list_type_1.append(sum_type_1/float(number_type_1))
            else:
                number_type_0 += 1
                sum_type_0 += value
                averages_list_type_0.append(sum_type_0/float(number_type_0))
        state = number_type_0, number_type_1, sum_type_0, sum_type_1
        return ([averages_list_type_0, averages_list_type_1], state)
                
    return stream_func(
        list_func=average_by_sensor_type_list,
        inputs=input_stream,
        num_outputs=2,
        state=(0, 0, 0.0, 0.0),
        call_streams=None)


def main():
    def print_stream_recent(s):
        print s.name, " = ", s.recent[:s.stop]

    x_stream = Stream('x')
    y_stream, z_stream = average_by_sensor_type_stream(x_stream)
    y_stream.set_name('y')
    z_stream.set_name('z')

    x_stream.extend([(0,2), (0,4), (1,5), (1,1), (1,3), (1,7), (1,9), (1,11)])
    print_stream_recent(y_stream)
    print_stream_recent(z_stream)

if __name__ == '__main__':
    main()

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
def outliers_and_inrange_streams(x_and_y_streams, delta):
    # List function: list of lists, state -> list of lists, state
    def outliers_and_inrange_lists(x_and_y_lists, state):
        x_list, y_list = x_and_y_lists
        a, b, n, x_sum, y_sum, xx_sum, xy_sum = state
        outliers_list = list()
        inrange_list = list()
        min_length = min(len(x_list), len(y_list))
        for i in range(min_length):
            if abs(a*x_list[i] + b - y_list[i]) > delta:
                outliers_list.append([x_list[i], y_list[i]])
            else:
                inrange_list.append([x_list[i], y_list[i]])

            n += 1
            x_sum += x_list[i]
            y_sum += y_list[i]
            xy_sum += x_list[i]*y_list[i]
            xx_sum += x_list[i] * x_list[i]
            a = (xy_sum - x_sum*y_sum/float(n))/(xx_sum - x_sum*x_sum/float(n))
            b = y_sum/float(n) - a*x_sum/float(n)
            state = a, b, n, x_sum, y_sum, xx_sum, xy_sum
        return ([inrange_list, outliers_list], state)
    
    return stream_func(
        list_func=outliers_and_inrange_lists,
        inputs=x_and_y_streams,
        num_outputs=2,
        state=(1.0, 0.0, 0, 0.0, 0.0, 0.001, 0.0),
        call_streams=None)



def main():
    def print_stream_recent(s):
        print s.name, " = ", s.recent[:s.stop]

    x_stream = Stream('x')
    y_stream = Stream('y')
    delta = 0.25
    inrange_stream, outliers_stream = \
      outliers_and_inrange_streams([x_stream, y_stream], delta)
    inrange_stream.set_name('in range')
    outliers_stream.set_name('outliers')

    x_stream.extend(range(10, 15, 1))
    y_stream.extend(range(11, 16, 1))
    print_stream_recent(x_stream)
    print_stream_recent(y_stream)
    print_stream_recent(inrange_stream)
    print_stream_recent(outliers_stream)

    x_stream.extend(range(15, 205, 1))
    y_stream.extend(range(17, 207, 1))
    print_stream_recent(x_stream)
    print_stream_recent(y_stream)
    print_stream_recent(inrange_stream)
    print_stream_recent(outliers_stream)
if __name__ == '__main__':
    main()

"""This module contains examples of the stateless single stream source
"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from ListOperators import stream_func

import random
def mean_and_sigma_streams(trigger_stream):
    # List function: state -> [list of lists, state]
    def mean_and_sigma_lists(state):
        number_of_values, sum_of_values, sum_of_squared_values = state
        next_value = random.random()
        number_of_values += 1
        sum_of_values += next_value
        sum_of_squared_values += next_value*next_value
        mean = sum_of_values/float(number_of_values)
        second_moment = sum_of_squared_values/float(number_of_values)
        variance = second_moment - mean*mean
        sigma = math.sqrt(variance)
        state = (number_of_values, sum_of_values, sum_of_squared_values)
        return ([[mean], [sigma]], state)
    
    return stream_func(
        list_func=mean_and_sigma_lists,
        inputs=None,
        num_outputs=2,
        state=(0, 0.0, 0.0),
        call_streams=[trigger_stream])



def main():
    def print_stream_recent(s):
        print s.name, " = ", s.recent[:s.stop]

    trigger_stream = Stream()

    mean_stream, sigma_stream = \
      mean_and_sigma_streams(trigger_stream)

    mean_stream.set_name('mean stream')
    sigma_stream.set_name('sigma stream')
    
    print 'before trigger'
    print_stream_recent(sigma_stream)
    print_stream_recent(mean_stream)
    
    trigger_stream.append(1)
    print 'after first trigger'
    print_stream_recent(sigma_stream)
    print_stream_recent(mean_stream)
    
    trigger_stream.append(1)
    print 'after second trigger'
    print_stream_recent(sigma_stream)
    print_stream_recent(mean_stream)
    

if __name__ == '__main__':
    main()

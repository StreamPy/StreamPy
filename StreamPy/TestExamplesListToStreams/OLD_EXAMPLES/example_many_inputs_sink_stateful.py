"""This module contains examples of the stateless single stream source
"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from ListOperators import stream_func

def print_is_multiple_with_scores_streams(multiples_and_divisors_streams):
    # List function: list of lists, state -> state
    def print_is_multiple_with_scores_lists(multiples_and_divisors_lists, state):
        multiples_list, divisors_list = multiples_and_divisors_lists
        num_true_values, num_false_values = state
        for i in range(min(len(multiples_list), len(divisors_list))):
            is_multiple = (multiples_list[i] % divisors_list[i] == 0)
            num_true_values += is_multiple
            num_false_values += (not is_multiple)
            print 'is {0} a multiple of {1} ? {2}. '.format(
                multiples_list[i], divisors_list[i],
                is_multiple)
            print 'Total number of true values = {0}, false values = {1}'.format(
                num_true_values, num_false_values)
        state = (num_true_values, num_false_values)
        return state

    return stream_func(
        list_func=print_is_multiple_with_scores_lists,
        inputs=multiples_and_divisors_streams,
        num_outputs=0,
        state=(0,0),
        call_streams=None)









def main():
    multiples_stream = Stream('multiples')
    divisors_stream = Stream('divisors')
    print_is_multiple_with_scores_streams([multiples_stream, divisors_stream])
    multiples_stream.extend([8, 27, 20, 11])
    divisors_stream.extend([4, 3, 7])
    multiples_stream.extend([13])
    divisors_stream.extend([2, 3, 5])

if __name__ == '__main__':
    main()

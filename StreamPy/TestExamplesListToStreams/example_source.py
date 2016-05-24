if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Stream import Stream, _no_value
from Operators import stream_func
import numpy as np
import random

def main():

    def single_stream_of_random_numbers(trigger_stream):
        def ran():
            return random.random()

        return stream_func(
            inputs=None,
            f_type='element',
            f=ran,
            num_outputs=1,
            call_streams=[trigger_stream])

    def stream_of_normal_and_pareto(clock_stream, b):
        from scipy.stats import norm, pareto

        def normal_and_pareto():
            return [norm.rvs(size=1)[0], pareto.rvs(b, size=1)[0]]

        return stream_func(
            inputs=None,
            f_type='element',
            f=normal_and_pareto,
            num_outputs=2,
            call_streams=[clock_stream]
            )


    trigger = Stream('trigger')
    r = single_stream_of_random_numbers(
        trigger_stream=trigger)
    u, v = stream_of_normal_and_pareto(
        clock_stream=trigger, b=2.62171653214)
    r.set_name('random')
    u.set_name('normal')
    v.set_name('pareto')

    trigger.extend(['tick', 'tick'])
    trigger.print_recent()
    r.print_recent()
    u.print_recent()
    v.print_recent()

if __name__ == '__main__':
    main()
        

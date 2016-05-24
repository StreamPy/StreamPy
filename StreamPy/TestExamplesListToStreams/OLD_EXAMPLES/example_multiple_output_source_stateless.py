"""This module contains examples of the stateless single stream source
"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from ListOperators import stream_func

def random_and_extreme_streams(trigger_stream):
    import random
    # List function: () -> list of lists
    def is_extreme(v):
        return v > 0.9 or v < 0.1

    def random_and_extreme_lists():
        x_list = [random.random() for _ in range(10)]
        extremes_list = filter(is_extreme, x_list)
        return [x_list, extremes_list]
    
    return stream_func(
        list_func=random_and_extreme_lists,
        inputs=None,
        num_outputs=2,
        state=None,
        call_streams=[trigger_stream])



def main():
    def print_stream_recent(s):
        print s.name, " = ", s.recent[:s.stop]

    trigger_stream = Stream()
    random_stream, extreme_stream = \
      random_and_extreme_streams(trigger_stream)

    random_stream.set_name('random stream')
    extreme_stream.set_name('extreme stream')
    
    print 'before trigger'
    print_stream_recent(random_stream)
    print_stream_recent(extreme_stream)
    
    trigger_stream.append(1)
    print 'after first trigger'
    print_stream_recent(random_stream)
    print_stream_recent(extreme_stream)
    
    trigger_stream.append(1)
    print 'after second trigger'
    print_stream_recent(random_stream)
    print_stream_recent(extreme_stream)
    

if __name__ == '__main__':
    main()

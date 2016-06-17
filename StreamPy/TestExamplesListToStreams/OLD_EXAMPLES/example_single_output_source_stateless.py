"""This module contains examples of the stateless single stream source
"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from ListOperators import stream_func

def single_random_stream(trigger_stream):
    # List function: () -> list
    import random
    def list_of_single_random_number():
        return [random.random()]

    return stream_func(
        list_func=list_of_single_random_number,
        inputs=None,
        num_outputs=1,
        state=None,
        call_streams=[trigger_stream])



def main():
    def print_stream_recent(s):
        print s.name, " = ", s.recent[:s.stop]

    trigger_stream = Stream()
    random_stream = single_random_stream(trigger_stream)
    random_stream.set_name('random stream')
    
    print 'before trigger'
    print_stream_recent(random_stream)
    
    trigger_stream.append(1)
    print 'after first trigger'
    print_stream_recent(random_stream)

    trigger_stream.append(1)
    print 'after second trigger'
    print_stream_recent(random_stream)
    

if __name__ == '__main__':
    main()

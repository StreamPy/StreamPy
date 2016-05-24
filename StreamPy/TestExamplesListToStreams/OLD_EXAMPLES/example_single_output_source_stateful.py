"""This module contains examples of the stateful single stream source
"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Agent import *
from ListOperators import stream_func
        
def stream_from_list(x_list, trigger_stream):
    # List function: state -> list, state
    def get_next_element(index):
        return ([x_list[index]], index+1)
    
    return stream_func(
        list_func=get_next_element,
        inputs=None,
        num_outputs=1,
        state=0, # initial state
        call_streams=[trigger_stream])

def main():
    def print_stream_recent(s):
        print s.name, " = ", s.recent[:s.stop]

    trigger_stream = Stream()
    x_list = [3, 7, 13]
    x_list_stream = stream_from_list(x_list, trigger_stream)
    x_list_stream.set_name('x_list stream')
    
    print 'before trigger'
    print_stream_recent(x_list_stream)
    
    trigger_stream.append(1)
    print 'after first trigger'
    print_stream_recent(x_list_stream)

    trigger_stream.append(1)
    print 'after second trigger'
    print_stream_recent(x_list_stream)
    

if __name__ == '__main__':
    main()

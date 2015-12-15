if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Stream import Stream
from Operators import stream_func
from instances import instance_dict
from components import *


random_7cd8t_out = generate_stream_of_random_integers()
split_ptc81_even, split_ptc81_odd = split_into_even_odd(random_7cd8t_out)
split_ptc81_even.set_name('split_ptc81_even')
split_ptc81_odd.set_name('split_ptc81_odd')
print_stream(split_ptc81_odd)
print_stream(split_ptc81_even)

if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Stream import Stream
from Operators import stream_func
from components_test import *
#from components import *

generate_stream_of_random_integers_PORT_output = generate_stream_of_random_integers()
generate_stream_of_random_integers_PORT_output.set_name('generate_stream_of_random_integers_PORT_output')
split_into_even_odd_stream_PORT_even, split_into_even_odd_stream_PORT_odd = split_into_even_odd_stream(generate_stream_of_random_integers_PORT_output)
split_into_even_odd_stream_PORT_even.set_name('split_into_even_odd_stream_PORT_even')
split_into_even_odd_stream_PORT_odd.set_name('split_into_even_odd_stream_PORT_odd')
print_value_stream(split_into_even_odd_stream_PORT_even)
print_value_stream(split_into_even_odd_stream_PORT_odd)

from nose.tools import assert_equals
from Operators import stream_func

output_test = []
def check(x, n):
    def check_value(x_element):
        print x_element
        assert len(n) > 0
        assert_equals(x_element,n.pop(0))
    output_test.append(n)
    stream_func(inputs = x, f = check_value, f_type = 'element', num_outputs = 0)

def check_empty():
    for output in output_test:
        assert len(output) == 0

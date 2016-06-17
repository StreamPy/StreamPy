if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Stream import Stream
from Stream import _no_value
from Operators import stream_func, stream_agent

def echo(in_stream, out_stream):
    def _copy(v):
        print 'echo, v = ', v
        return v
    return stream_agent(
        inputs=in_stream,
        outputs= out_stream,
        f_type='element',
        f=_copy)

def echo_list(in_stream, out_stream):
    def _copy(lst):
        print 'echo, lst = ', lst
        return lst
    return stream_agent(
        inputs=in_stream,
        outputs= out_stream,
        f_type='list',
        f=_copy)

def add_count(in_stream, out_stream):
    def _add(v,count):
        print 'output is ', v+1
        return (v+1, count+1)
    return stream_agent(
        inputs=in_stream,
        outputs= out_stream,
        f_type='element',
        f=_add,
        state=0)

def echo_n_times(in_stream, out_stream, n):

    def echo_value(v,count):
        if count < n:
            print 'echo_value. receive', v
            count += 1
            return(v+1, count)
        else:
            return(_close, count)

    return stream_agent(
        inputs=in_stream,
        outputs=out_stream,
        f_type='element',
        f=echo_value,
        state=0)

def splitter(in_stream, out_streams):
    def number_even_odd(m):
        if m%2:
            # since n is odd, the zero-th element is
            # _no_value, and the first element is n
            # in the returned list
            return [_no_value, m]
        else:
            # since n is even, the zero-th element is
            # n, and the first element is _no_value
            # in the returned list.            
            return [m, _no_value]
        return stream_agent(
        inputs=in_stream,
        outputs=[out_stream_0, out_stream_1],
        f_type='element',
        f=number_even_odd)


if __name__ == '__main__':
    s = Stream(name='in',
               initial_value=[1])
    print 's.stop =', s.stop
    t = Stream(name='out')
    s.print_recent()
    t.print_recent()
    echo_list(s, t)
    s.print_recent()
    t.print_recent()
    print splitter(s, t)
    



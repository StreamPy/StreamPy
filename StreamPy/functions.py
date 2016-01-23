def random_ints(input_streams, output_streams):
    from random import randint
    from Stream import Stream, _close, _no_value
    from Operators import stream_agent, stream_agent
    # Append random numbers to output_streams[0]
    # The numbers are in the interval (0, 99).
    N = 10
    for i in range(N):
        element_of_stream = randint(0,99)
        output_streams[0].append(element_of_stream)
        print 'In random_ints. element = ', element_of_stream
        #time.sleep(0.1)

    # Close this stream
    output_streams[0].append(_close)

# The single output stream returns the function f
# applied to elements of the single input stream.
# When the input stream is closed, also close the
# output stream.
def apply_func_agent(input_streams, output_streams):
    from Stream import Stream, _close, _no_value
    from Operators import stream_agent, stream_agent

    def f(v): return 2*v

    input_stream = input_streams[0]
    output_stream = output_streams[0]

    def apply_func(v):
        # When the input stream is closed, return
        # _close to cause the output stream to close.
        if v == _close:
            return _close
        else:
            print "Apply func"
            return f(v)

    return stream_agent(
        inputs=input_stream,
        outputs=output_stream,
        f_type='element',
        f=apply_func)


# Print the values received on the input stream.
def print_agent(input_streams, output_streams):
    from Stream import Stream, _close, _no_value
    from Operators import stream_agent, stream_agent
    input_stream = input_streams[0]

    def p(v):
        if v != _close:
            print 'print_agent', input_stream.name, v

    return stream_agent(
        inputs=input_stream,
        outputs=[],
        f_type='element',
        f=p)

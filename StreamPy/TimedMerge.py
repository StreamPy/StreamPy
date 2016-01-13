
from Stream import Stream, _no_value, _multivalue
from Agent import Agent
from examples_element_wrapper import print_stream
from Operators import assert_is_list_of_streams_or_None, assert_is_list_of_streams


def timed_merge_agent(list_of_input_streams, single_output_stream, call_streams=None):
    """
    This function creates an agent that merges the input streams into a single output
    stream where the timestamps of the output stream are in monotone nondecreasing
    order.
    Elements of the input streams are tuples (timestamp, ....); we require the zeroth
    part of the tuple to be a timestamp: a nonnegative number.

    Parameters
    ----------
    list_of_input_streams: a nonempty list of streams
        Elements of the input streams are tuples in which the zeroth element is a
        timestamp: a nonnegative number
    single_output_stream: a single stream
    call_streams: optional
        call_streams is either None or a list of streams.

    Returns
    -------
         An agent that merges the input streams into an output stream.

    """
    assert_is_list_of_streams_or_None(call_streams)
    assert_is_list_of_streams(list_of_input_streams)
    assert isinstance(single_output_stream, Stream)

    def transition(in_lists, last_time):
        input_lists = [v.list[v.start:v.stop] for v in in_lists]
        output, last_time, indices = timed_merge(input_lists, last_time)
        in_lists_start_values = [in_lists[j].start + indices[j]
                                 for j in range(len(in_lists))]
        print 'in_lists_start_values', in_lists_start_values
        return ([output], last_time, in_lists_start_values)
    
    # Create agent
    last_time = -1
    return Agent(list_of_input_streams, [single_output_stream],
          transition, last_time, call_streams)

def timed_merge(input_lists, last_time):
    assert all([
        ((not input_list) or input_list[0][0] >= last_time
         for input_list in input_lists)])
    output = list()
    range_in = range(len(input_lists))

    # MERGE SORT
    # input_lists[j][indices[j]] is the element inspected
    # for the j-th input stream, at each iteration.
    indices = [0 for _ in range_in]
    # The iteration has already output input_lists[j][k] for
    # k < indices[j]. It now inspects input_lists[j][indices[j]].
    while all([len(input_lists[j]) > indices[j] for j in range_in]):
        # last_time is the smallest time that has not been output yet.
        last_time = min([input_lists[j][indices[j]][0] for j in range_in])
        # Output all inputs with timestamp equal to last_time.
        # This is a step in merge_sort.
        for j in range_in:
            if input_lists[j][indices[j]][0] == last_time:
                output.append(input_lists[j][indices[j]])
                indices[j] += 1

    return (output, last_time, indices)

def main():
    x = Stream('x')
    y = Stream('y')
    z = Stream('z')
    print_stream(x)
    print_stream(y)
    print_stream(z)
    
    timed_merge_agent([x,y], z)

    x.extend([(1, 'a'), (3, 'b'), (3, 'c'), (10, 'd'), (15, 'e'), (17, 'f')])
    y.extend([(2, 'A'), (3, 'B'), (3, 'C'), (9, 'D'), (20, 'E')])

    t = Stream('t')
    u = Stream('u')
    v = Stream('v')
    w = Stream('w')
    print_stream(t)
    print_stream(u)
    print_stream(v)
    print_stream(w)
    
    timed_merge_agent([u,v], w, call_streams=[t])

    u.extend([(1, 'a'), (3, 'b'), (3, 'c'), (10, 'd'), (15, 'e'), (17, 'f')])
    v.extend([(2, 'A'), (3, 'B'), (3, 'C'), (9, 'D'), (20, 'E')])
    t.append(0)
    u.extend([(21, 'g'), (23, 'h'), (33, 'i'), (40, 'j'), (50, 'K')])
    v.extend([(22, 'F'), (23, 'G'), (43, 'H'), (51, 'I'), (59, 'J')])
    t.append(0)
if __name__ == '__main__':
    main()

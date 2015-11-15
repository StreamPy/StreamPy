"""This module has functions that convert operations on standard Python data structures
to operations on streams.

The module has three collections of functions:
(1) functions that convert operations on standard Python data structures
to operations on streams. These functions operate on a list of input
streams to generate a list of output streams. The functions deal with
the following data structures:
  (a) lists,
  (b) individual elements of lists,
  (c) sliding windows, and
  (d) timed windows.
(2) functions that map the general case of multiple input streams and
multiple output streams described above to the following special cases:
  (a) merge: an arbitrary number of input streams and a single output stream.
  (b) split: a single input stream and an arbitrary number of output streams.
  (c) op: a single input stream and a single output stream.
  (d) source: no input and an arbitrary number of output streams.
  (e) sink: no ouput and an arbitrary number of input streams.
  These special cases simplify functions that need to be written
  for standard Python data structures. You can always use the multiple
  inputs and outputs case even if there is only one or no input
  or output; however, the functions for merge, split, op, source, and sink
  are simpler than the multiple input and output case.
(3) a function that provides a single common signature for converting
operations on Python structures to operations on streams regardless of
whether the function has no inputs, a single input stream, a list of
input streams, or no outputs, a single output stream or a list of output
streams.
(12 October 2015. Mani. Changed initialization of output_lists.)
"""

from Agent import Agent
from Stream import Stream, StreamArray

from Stream import _no_value, _multivalue, _close, TimeAndValue

# ASSERTIONS USED IN FILE
def assert_is_list_of_streams_or_None(x):
    assert isinstance(x, list) or isinstance(x, tuple) or x is None,\
      'Expected {0} to be None or list or tuple.'.format(x)
    if x is not None:
        assert all(isinstance(l, Stream) for l in x),\
          'Expected {0} to be a list (or tuple) of streams.'.format(x)

def assert_is_list_of_streams(x):
    assert isinstance(x, list) or isinstance(x, tuple),\
      'Expected {0} to be a list or tuple'.format(x)
    assert all(isinstance(l, Stream) for l in x),\
      'Expected {0} to be a list (or tuple) of streams'.format(x)

def assert_is_list_of_lists(x, list_size=None):
    assert isinstance(x, list) or isinstance(x, tuple),\
      'Expected {0} to be a list or tuple'.format(x)
    assert all((isinstance(l, list) or isinstance(l, np.ndarray)) for l in x),\
      'Expected {0} to be a list (or tuple) or np.ndarray of lists'.format(x)
    assert list_size is None or list_size == len(x), \
      'Expected len({0}) == {1}, or {1} to be None'.format(x, list_size)

def assert_is_list_or_None(x):
    assert isinstance(x, list) or x is None, \
      'Expected {0} to be a list or None'.format(x)

def assert_is_list(x):
    assert isinstance(x, list), \
      'Expected {0} to be a list'.format(x)

def remove_novalue_and_open_multivalue(l):
    """ This function returns a list which is the
    same as the input parameter l except that
    (1) _no_value elements in l are deleted and
    (2) each _multivalue element in l is opened
        i.e., for an object _multivalue(list_x)
        each element of list_x appears in the
        returned list.

    Parameter
    ---------
    l : list
        A list containing arbitrary elements
        including, possibly _no_value and
        _multi_value

    Returns : list
    -------
        Same as l with every _no_value object
        deleted and every _multivalue object
        opened up.

    Example
    -------
       l = [0, 1, _no_value, 10, _multivalue([20, 30])]
       The function returns:
           [0, 1, 10, 20, 30]

    """

    if not isinstance(l, list):
        return l

    return_list = []
    for v in l:
        if v == _no_value:
            continue
        elif isinstance(v, _multivalue):
            return_list.extend(v.lst)
        else:
            return_list.append(v)
    return return_list


"""PART 1 OF MODULE
This part consists of functions that convert operations
on conventional data structures to operations on streams.
The functions are of two types:
(1) functions that return agents
      e.g., list_agent, element_agent, window_agent,
            dynamic_window_agent, timed_agent
(2) functions that return streams
      e.g., list_func, element_func, window_func,
           dynamic_window_func, timed_func

Functions that return agents have the following parameters:
f, inputs, num_outputs, state, call_streams, window_size,
step_size.

Parameters
----------
inputs : list of streams
        The streams read by this agent.
        inputs may be an empty list. (For example a data
        source may not read any stream.)
        inputs corresponds to parameter in_streams of agent.
outputs : list of streams.
        The streams written by this agent.
        outputs may be an empty list.
        outputs corresponds to parameter out_streams of agent.
state : object
        The state of the agent
call_streams : list of streams
        See call_streams in agent
window_size : positive integer or None
        For moving window operations, this is the size of
        the window. The size is the number of elements in
        the window.
        window_size is None for operations that are not on
        windows. For example, if the operation is on a single
        element of a stream then window_size should be None
        rather than 1 even though a window_size of 1 would work.
step_size : positive integer or None
        step_size is the distance that a window is moved on
        each step.
f : function
        The function executed in a state transition.
        Inputs to the function:
         (1) A list of objects where the length of the list
             is the number of input streams of the agent,
             and where the object depends on the type of
             wrapper used to convert f to a function on
             streams. The objects are either elements of
             the stream or windows into the stream.
         (2) The state of the agent before a state transition.
        Outputs of the function:
         (1) A list of objects where the length of the list
             is the number of output streams of the agent.
             The j-th object in the list is appended to the
             j-th output stream of the agent.
         (2) The state of the agent after the transition.

Notes
-----
The structure of each of these functions is as follows:
The functions element_agent, window_agent, timed_agent
create agents. The functions element_func, window_func,
timed_func call element_agent, window_agent, timed_agent
(respectively) to create agents and also to create their
output streams. The functions element_func, window_func,
and timed_func are syntactic sugar; they are convenient
for functional composition.

"""

####################################################
# OPERATIONS ON LISTS
####################################################

def list_agent(f, inputs, outputs, state, call_streams,
              window_size, step_size):
    assert_is_list_of_streams_or_None(call_streams)

    def transition(in_lists, state):
        smallest_list_length = min(v.stop - v.start for v in in_lists)
        input_lists = [v.list[v.start:v.start+smallest_list_length] for v in in_lists]
        if not input_lists:
            return ([[]]*num_outputs, state, [v.start for v in in_lists])
        if state is None:
            output_lists = f(input_lists)
        else:
            output_lists, state = f(input_lists, state)

        ## if num_outputs:
        ##     assert_is_list_of_lists(output_lists, num_outputs)
        in_lists_start_values = [v.start+smallest_list_length for v in in_lists]
        return (output_lists, state, in_lists_start_values)

    # Create agent
    Agent(inputs, outputs, transition, state, call_streams)

def list_func(f, inputs, num_outputs, state, call_streams,
              window_size, step_size):
    outputs = [Stream() for i in range(num_outputs)]
    list_agent(f, inputs, outputs, state, call_streams,
              window_size, step_size)
    return outputs


####################################################
# OPERATIONS ON SIMPLE ELEMENTS
####################################################
def element_agent(f, inputs, outputs, state, call_streams,
                 window_size, step_size):

    assert_is_list_of_streams_or_None(call_streams)
    num_outputs = len(outputs)

    def transition(in_lists, state):
        input_lists = zip(*[v.list[v.start:v.stop] for v in in_lists])
        # If the new input data is empty then return empty lists for
        # each output stream, and leave the state and the starting point
        # for each input stream unchanged.
        if not input_lists:
            return ([[]]*num_outputs, state, [v.start for v in in_lists])

        #list_of_output_list[i] will be set to the output value
        # corresponding to the i-th value in each of the input
        # streams
        list_of_output_list = list()
        for _ in range(len(input_lists)):
            list_of_output_list.append(list())
        for i,input_list in enumerate(input_lists):
            if state is None:
                output_list = f(input_list)
            else:
                output_list, state = f(input_list, state)
            # The output_list returned by f must have
            # one element for each output stream.
            # The output list must be a list; so convert
            # None values (for sinks) into empty lists.
            if output_list is None: output_list = []
            list_of_output_list[i] = output_list

        # This function has at least one output because the sink case
        # was considered in the last line.
        # list_of_output_list[i] is a list with one element for each output stream.
        # zip them up to get output_lists where output_lists[j] is the list that
        # gets appended to output stream j.
        output_lists = [list(v) for v in zip(*list_of_output_list)]
        # Remove _no_value elements from the output list because they do not
        # appear in streams.
        # Open up _multivalue([a,b]) into separate a, b values.
        output_lists = \
          [remove_novalue_and_open_multivalue(l) for l in output_lists]
        return (output_lists, state, [v.start+len(input_lists) for v in in_lists])

    # Create agent
    Agent(inputs, outputs, transition, state, call_streams)

def element_func(f, inputs, num_outputs, state, call_streams,
                 window_size, step_size):
    outputs = [Stream() for i in range(num_outputs)]
    element_agent(f, inputs, outputs, state, call_streams,
                  window_size, step_size)
    return outputs


####################################################
# OPERATIONS ON WINDOWS
####################################################

def window_agent(f, inputs, outputs, state, call_streams,
                window_size, step_size):
    num_outputs = len(outputs)
    #f: list, state -> element, state
    def transition(in_lists, state=None):
        range_out = range((num_outputs))
        range_in = range(len(in_lists))
        # This function will set the k-th element of output_lists
        # to the value to be output on the k-th output stream.
        output_lists = list()
        for _ in range_out:
            output_lists.append([])
        # Avoids problems with output_list = [ [] for _ in range_out ]
        # window_starts is the list of starting indices for the
        # window in each input stream.
        window_starts = [in_list.start for in_list in in_lists]

        smallest_list_length = min(v.stop - v.start for v in in_lists)
        if window_size > smallest_list_length:
            # Do not have enough elements in an input stream
            # for an operation on the window.
            # So no changes are made.
            return (output_lists, state, window_starts)

        # Each input stream has enough elements for a window operation.

        # num_steps is the number of window operations that can be
        # carried out with the given numbers of unprocessed elements
        # in the input streams.
        num_steps = (smallest_list_length - window_size)/step_size
        for i in range(num_steps):
            # Calculate the output, 'increments', for this window operation.
            # windows is a list with a window for each input stream.
            # increments is a list with an element for each output stream.
            # increments[k] will be appended to the k-th output stream
            # by this function.
            # The window for the j-th input stream starts at window_starts[j]
            # and ends at window_starts[j]+window_size.
            # in_lists[j].list is the list of messages on the j-th input stream.
            windows = [in_lists[j].list[window_starts[j]:window_starts[j]+window_size] \
                       for j in range_in]
            if state is None:
                increments = f(windows)
            else:
                increments, state = f(windows, state)

            # Remove _no_value and open up _multivalue elements in
            # each [increments[k]].
            # For example, _multivalue([11, 5, 9]) object will be
            # added to the stream as three separate messages,
            # 11, 5 and 9.
            # Note that increments[k] is a value to be appended to
            # the output stream. The function remove_novalue has
            # a parameter which is a list. So we call the function
            # with parameter [increments[k]] rather than increments[k]
            # and we extend output_lists[k] rather than append to it.
            for k in range_out:
                output_lists[k].extend(
                    remove_novalue_and_open_multivalue([increments[k]]))

            window_starts = [v+step_size for v in window_starts]

        in_lists_start_values = [in_list.start + num_steps*step_size for in_list in in_lists]
        return (output_lists, state, in_lists_start_values)

    # Create agent
    #output_streams = [Stream() for v in range(num_outputs)]
    Agent(inputs, outputs, transition, state, call_streams)
    #return output_streams

def window_func(f, inputs, num_outputs, state, call_streams,
                window_size, step_size):
    outputs = [Stream() for i in range(num_outputs)]
    window_agent(f, inputs, outputs, state, call_streams,
                  window_size, step_size)
    return outputs

####################################################
# OPERATIONS ON DYNAMIC WINDOWS
####################################################

def dynamic_window_agent(f, input_stream, output_stream, state,
                         min_window_size, max_window_size, step_size):
    # state is a list where state[0] must be current_window_size
    # state[1] is a boolean value, steady_state which
    # indicates whether the max window size has been reached.
    # reset is a boolean which is set to True when the window
    # is to be reset to the min window size.
    # state[3:] is defined by the user.
    # current_window_size is state[0]
    # steady_state is state[1]
    # reset is state[2]

    # This function produces a single output stream.
    num_outputs = 1

    def transition(in_lists, state):
        current_window_size = state[0]
        steady_state = state[1]
        reset = state[2]
        reset_increment = 0
        # output_list is the list of messages that will be
        # sent on the output stream in this transition.
        output_list = list()
        # input is the list of messages in the input
        # stream that are the input for this transition.
        # start, stop are pointers to the input stream
        # where input begins at start and ends at stop.
        input_in_list = in_lists[0]
        start = input_in_list.start
        stop = input_in_list.stop
        input = input_in_list.list[start:stop]
        input_length = stop - start
        if input_length < step_size:
            # Insufficient number of new messages in the input
            # stream for a transition.
            # No change
            return ([output_list], state, [start])

        # Increase the current window size in increments
        # of step size, and ensure it does not exceed
        # max window size.

        # input[start_increment:start_increment+current_window_size]
        # is the current window.
        # start_increment is initially 0 and remains 0 until the
        # current window size equals the max window size, and after
        # that point the start_increment is increased by the step size.
        start_increment = 0
        for i in range(0, input_length, step_size):
            ## if not steady_state:
            ##     current_window_size += step_size
            if current_window_size < min_window_size:
                # The current window size is too small
                # for a window calculation.
                current_window_size += step_size
                continue

            # Assert current_window_size >= min_window_size
            # Ensure that current window size does not exceed max value.
            current_window_size = min(current_window_size, max_window_size)

            if start_increment+ reset_increment + current_window_size > input_length:
                # Insufficient unprocessed messages in the input stream
                # for the next window.
                break

            # input_window is the next window in the input stream.
            input_window = input[
                start_increment+reset_increment:start_increment+reset_increment+current_window_size]

            # Compute increments to the output stream
            # Note: function f MUST return state (where state[0]
            # is the current_window_size and state[1] indicates whether
            # the steady state, i.e., current window size equals max value,
            # has been reached.
            # Update the state to reflect the new value of current_window_size
            state[0] = current_window_size
            state[1] = steady_state
            state[2] = reset

            # Compute the new output
            output_increment, state = f(input_window, state)
            current_window_size = state[0]
            steady_state = state[1]
            reset = state[2]
            if reset and steady_state:
                steady_state = False
                reset = False
                start_increment += current_window_size - min_window_size
                current_window_size = min_window_size - step_size
                ## reset_increment += start_increment
                ## reset_increment += max(0, current_window_size - min_window_size)
                ## start_increment = 0

            if not steady_state:
                # The start increment does not change because
                # the starting point of the window remains
                # unchanged until the current window size increases
                # to the max window size. After that point,
                # the starting point of the window moves forward
                # by step size.
                #start_increment = 0
                if current_window_size >= max_window_size - step_size:
                    steady_state = True
                    start_increment += current_window_size - (max_window_size - step_size)
                    current_window_size = max_window_size
                else:
                    current_window_size += step_size
                    #start_increment = 0
            else:
                start_increment += step_size
                current_window_size = max_window_size

            # Deal with special objects that should not be placed
            # on the output stream.
            output_increment = remove_novalue_and_open_multivalue(
                [output_increment])
            # Place the output increment on the output list.
            # The messages in the output list will eventually
            # be sent on the output stream
            output_list.extend(output_increment)

        # The start pointer for the input stream is moved forward
        # to the starting point of the current window
        start += start_increment
        start_increment = 0

        # Update state
        state[0] = current_window_size
        state[1] = steady_state
        state[2] = reset

        return ([output_list], state, [start])

    # Create agent
    Agent([input_stream], [output_stream], transition, state)



def dynamic_window_func(f, inputs, state,
                min_window_size, max_window_size, step_size):
    output_stream = Stream()
    dynamic_window_agent(
        f, inputs, output_stream, state,
        min_window_size, max_window_size, step_size)
    return output_stream


####################################################
# OPERATIONS ON TIMED WINDOWS
####################################################

def list_index_for_timestamp(in_list, start_index, timestamp):
    """ A helper function for timed operators.
    The basic idea is to return the earliest index in
    in_list.list[start_index:in_list.stop] with a time field
    that is greater than or equal to timestamp. If no such index
    exists then return a negative number.

    Parameters
    ----------
    in_list: InList
             InList = namedtuple('InList', ['list', 'start', 'stop'])
             A slice into a stream.
    start_index: nonnegative integer
             A pointer into in_list.list
    timestamp: number

    Returns
    -------
    Returns positive integer i where:
    either: 'FOUND TIME WINDOW IN IN_LIST'
        i >= start_index and
        i <= in_list.stop  and
        (in_list[start_index] >= timestamp
        or
        in_list.list[i-2].time < timestamp <= in_list.list[i-1].time
        )

        )
    or: 'NO TIME WINDOW IN IN_LIST'
        i < 0 (negative i indicates no time window) and
           (in_list.list[in_list.stop-1] <= timestamp
                       or
           the list is empty, i.e.
           (in_list.start = in_list.stop)

    Requires
    --------
         start_index >= in_list.start and
         start_index < in_list.stop

    """
    # If the list is empty then return a negative number to indicate
    # absence of time window.
    if in_list.start == in_list.stop:
        return -1

    if start_index < in_list.start or start_index >= in_list.stop:
        raise Exception('start_index out of range: start_index =', start_index,
                        ' in_list.start = ', in_list.start,
                        ' in_list.stop = ', in_list.stop)

    for i in range(start_index, in_list.stop):
        # assert i <= in_list.stop-1
        if in_list.list[i].time >= timestamp:
            # Found an index i with a sufficiently large time.
            return i

    # All the times in in_list up to in_list.stop are less
    # than timestamp.
    # assert in_list.list[in_list.stop - 1] < timestamp
    return -1 # Return a negative number to indicate absence of time window.


def timed_agent(f, inputs, outputs, state, call_streams,
               window_size, step_size):
    # inputs is a list of lists of TimeAndValue pairs with
    # one list of TimeAndValue pairs for each input stream.
    # num_outputs is the number of output streams
    num_outputs = len(outputs)
    range_out = range(num_outputs)
    # num_inputs is the number of input streams.
    num_inputs = len(inputs)
    range_in = range(num_inputs)
    window_start_time = 0
    # state is the state of the underlying agent.
    # Augment the state with the start time of the
    # window; window times will be the times of
    # TimeAndValue objects in the output streams.
    combined_state = (window_start_time, state)

    def transition(in_lists, combined_state):
        window_start_time, state = combined_state
        output_lists = list()
        # output_lists is a list of lists.
        # output_lists has one list for each output stream.
        for _ in range_out:
            output_lists.append([])
        window_end_time = window_start_time + window_size
        window_start_indexes = [ in_lists[j].start for j in range_in]

        # Each iteration of the while loop carries out a
        # calculation for one time window. At each successive
        # iteration, the time window is moved forward by the
        # step size. Both the window_size and step_size refer
        # to time rather than the number of elements in the
        # window.
        # The while loop breaks when the next time window does
        # not span all input streams, i.e. when the time stamps
        # for some input stream aren't greater than or equal
        # to the end-time of the time window.
        while True:
            # window_end_indexes is a list whose j-th
            # element is either:
            # (1) the earliest index in the j-th
            # input list for which the stream element's time
            # is window_end_time or greater, or
            # (2) is a negative number if no such element
            # exists in the list.
            # In case (1) we have found a time window
            # within this in_list, and in case (2)
            # no time window exists within the in_list.
            window_end_indexes = [list_index_for_timestamp(
                in_lists[j],
                window_start_indexes[j],
                window_end_time) for j in range_in]
            # If any time window is empty then do not
            # carry out computations across the time windows
            # of all the input streams. Return with no change
            # to window_start_time or the state, and with
            # the output_list for each stream set to the empty
            # list.
            if any(window_end_indexes[j] < 0 for j in range_in):
                break

            # Assert no time-window is empty.
            # So, for each input stream j:
            # window_end_indexes[j] > window_start_indexes[j]
            windows = [in_lists[j].list[window_start_indexes[j]: \
                                       window_end_indexes[j]] for j in range_in]
            # windows is a list of num_inputs lists where:
            # windows[j] is a list of TimeAndValue objects.
            # Function f returns a list of num_outputs elements,
            # one element for each output stream. These elements
            # are usually objects other than TimeAndValue objects.
            # increments[k] is the output element appended to
            # the k-th output stream. increments[k] is a single object
            # (and not necessarily a list).
            if state is None:
                increments = f(windows)
            else:
                increments, state = f(windows, state)

            # The output list for each output stream contains TimeAndValue objects.
            # The time field associated with increments[k] for all k is the
            # window end time; so, all the messages on all the output streams
            # associated with this input time-window have the same time-value.
            for k in range_out:
                output_lists[k].append(TimeAndValue(window_end_time, increments[k]))

            # Increment the window start and end times by step size (which is also
            # in units of time).
            window_start_time += step_size
            window_end_time += step_size

            # Compute how far forward (measured in numbers of
            # elements) the windows can move for each input
            # stream.
            # new_window_start_indexes[j] is the index
            # of the start of the next window, IF all windows
            # move forward.
            new_window_start_indexes = [list_index_for_timestamp(
                in_lists[j],
                window_start_indexes[j],
                window_start_time) for j in range_in]

            # Exit the while-TRUE loop if a window on any stream
            # cannot move forward because the stream doesn't have
            # any more new data. This is indicated by a negative
            # value for new_window_start_indexes[j] for stream j.
            if any(new_window_start_indexes[j] < 0 for j in range_in):
                break
            ## #CHECKING FOR PROGRESS TOWARDS TERMINATION
            ## if (any(new_window_start_indexes[j] < window_start_indexes[j]
            ##        for j in range_in) or
            ##        all(new_window_start_indexes[j] == window_start_indexes[j]
            ##        for j in range_in)):
            ##     raise Exception('TimedOperator: start_indexes')
            window_start_indexes = new_window_start_indexes

        combined_state = (window_start_time, state)
        # return output messages, the new state, and the new start values of
        # the input streams.
        return (output_lists, combined_state, window_start_indexes)

    # Create agent
    combined_state = (window_start_time, state)
    Agent(inputs, outputs, transition, combined_state)


def timed_func(f, inputs, num_outputs, state, call_streams,
                window_size, step_size):
    outputs = [Stream() for i in range(num_outputs)]
    timed_agent(f, inputs, outputs, state, call_streams,
                  window_size, step_size)
    return outputs


####################################################
# OPERATIONS ON ASYCHRONOUS INPUT STREAMS
####################################################
def asynch_element_agent(
        f, inputs, outputs, state, call_streams,
        window_size, step_size):

    num_outputs = len(outputs)
    assert_is_list_of_streams_or_None(call_streams)

    def transition(in_lists, state):
        # output_lists[j] will be sent on output stream j
        output_lists = list()
        for _ in range(num_outputs):
            output_lists.append([])
        # If the input data is empty, i.e., if v.stop == v.start for all
        # v in in_lists, then return empty lists for  each output stream,
        # and leave the state and the starting point for each input
        # stream unchanged.
        if all(v.stop <= v.start for v in in_lists):
            return (output_lists, state, [v.start for v in in_lists])

        # Assert at least one input stream has unprocessed data.
        for stream_number, v in enumerate(in_lists):
            # if v.stop <= v.start then skip this input stream
            # because no new messages have arrived on this stream.
            if v.stop > v.start:
                # Carry out a state transition for this input
                # stream.
                # In the following,input_list is the list of new values
                # on this input stream. Compute the incremental list
                # generated by each element in input list due to a
                # transition, i.e., an execution of f.
                input_list = v.list[v.start:v.stop]
                # In the following, output_lists_increment is a list
                # with length num_outputs. It is a list even when
                # num_outputs is 0 or 1.
                # Process each unprocessed message (element) in this
                # input stream. output_lists_increment[k] is the message
                # to be sent on outputs[k] due to the incoming message
                # (element). Note that output_lists_increment[k] is an
                # element and not a list of elements.
                for element in input_list:
                    if state is None:
                        output_lists_increment = \
                          f((element, stream_number))
                    else:
                        # This function has state.
                        output_lists_increment, state = \
                          f((element, stream_number), state)

                    assert len(output_lists_increment) == num_outputs
                    for k in range(num_outputs):
                        # first remove _no_value and open up _multivalue
                        output_lists_increment[k] = \
                          remove_novalue_and_open_multivalue(
                              [output_lists_increment[k]])
                        output_lists[k].extend(output_lists_increment[k])

        return (output_lists, state, [v.stop for v in in_lists])

    # Create agent
    Agent(inputs, outputs, transition, state, call_streams)


def asynch_element_func(
        f, inputs, num_outputs, state, call_streams=None,
        window_size=None, step_size=None):

    assert_is_list_of_streams_or_None(call_streams)

    def transition(in_lists, state):
        # If the input data is empty then return empty lists for
        # each output stream, and leave the state and the starting point
        # for each input stream unchanged.
        if all(v.stop <= v.start for v in in_lists):
            return ([[]]*num_outputs, state, [v.start for v in in_lists])

        # Assert at least one input stream has unprocessed data.

        # output_lists[j] will be sent on output stream j
        output_lists = []
        for _ in range(num_outputs):
            output_lists.append([])
        #output_lists = [[]]*num_outputs
        for stream_number, v in enumerate(in_lists):
            # if v.stop <= v.start then skip this input stream
            if v.stop > v.start:
                # Carry out a state transition for this input
                # stream.
                # input_list is the list of new values on this
                # stream. Compute the incremental list generated
                # by each element in input list due to a transition,
                # i.e., an execution of f.
                input_list = v.list[v.start:v.stop]
                for element in input_list:
                    if state is None:
                        output_lists_increment = \
                          f((element, stream_number))
                    else:
                        # This function has state.
                        output_lists_increment, state = \
                          f((element, stream_number), state)
                    for k in range(num_outputs):
                        output_lists_increment[k] = \
                          remove_novalue_and_open_multivalue(
                              [output_lists_increment[k]])
                        output_lists[k].extend(output_lists_increment[k])

        return (output_lists, state, [v.stop for v in in_lists])


    # Create agent
    output_streams = [Stream() for i in range(num_outputs)]
    Agent(inputs, output_streams, transition, state, call_streams)
    return output_streams

"""
PART 2 OF MODULE.
Functions that map the general case of an arbitrary
number of input streams and an arbitrary number of output streams
to the following special cases:
  (1) merge: multiple input streams, single output stream
  (2) split: single input stream, multiple output streams
  (3) op: single input stream, single output stream
  (4) source: no input stream, single output stream
  (5) sink: single input stream, no output streams.

Each of these functions has the following parameters:
f, h, in_streams, window_size, step_size, state, call_streams.

Parameters
----------
f_type: str
   function on a standard Python data structure such as an
   integer or a list.
f: A general case (muti-input, multi-output) function.
in_streams: A list of input streams
window_size: Either None or a positive integer
step_size: None if the window_size is None, otherwise a positive
          integer.
state: The state of the computation.
call_streams: A list of streams. When a value is appended to any
      stream in this list, the function is executed.

"""


def h(f_type, *args):
    """ Calls the appropriate wrapper function given
    the name of the wrapper. The wrapper functions are
    list_func, element_func, window_func, ... for
    wrapper names 'list', 'element', 'window',..

    """
    if f_type is 'list':
        return list_func(*args)
    elif f_type is 'element':
        return element_func(*args)
    elif f_type is 'window':
        return window_func(*args)
    elif f_type is 'timed':
        return timed_func(*args)
    elif f_type is 'asynch_element':
        return asynch_element_func(*args)
    else:
        return 'no match'


def h_agent(f_type, *args):
    """ Calls the appropriate wrapper function given
    the name of the wrapper.  The wrapper functions are
    list_agent, element_agent, window_agent, ... for
    wrapper names 'list', 'element', 'window',..

    """
    if f_type is 'list':
        return list_agent(*args)
    elif f_type is 'element':
        return element_agent(*args)
    elif f_type is 'window':
        return window_agent(*args)
    elif f_type is 'timed':
        return timed_agent(*args)
    elif f_type is 'asynch_element':
        return asynch_element_agent(*args)
    else:
        return 'no match'


def many_to_many(f_type, f, in_streams, num_outputs, state,
                 call_streams, window_size, step_size):
    def g(x, state=None):
        if state is None: return f(x)
        else:
            output, new_state = f(x, state)
        return (output, new_state)

    out_streams = h(f_type, g, in_streams, num_outputs, state,
                    call_streams, window_size, step_size)
    return out_streams

def many_to_many_agent(f_type, f, in_streams, out_streams, state,
                 call_streams, window_size, step_size):
    def g(x, state=None):
        if state is None: return f(x)
        else:
            output, new_state = f(x, state)
            return (output, new_state)

    h_agent(f_type, g, in_streams, out_streams,
            state, call_streams, window_size, step_size)



def merge(f_type, f, in_streams, state, call_streams, window_size, step_size):
    def g(x, state=None):
        if state is None: return [f(x)]
        else:
            output, new_state = f(x, state)
            return ([output], new_state)

    out_streams = h(f_type, g, in_streams, 1, state, call_streams,
                    window_size, step_size)
    return out_streams[0]

def merge_agent(f_type, f, in_streams, out_stream,
                state, call_streams,
                window_size, step_size):
    def g(x, state=None):
        if state is None: return [f(x)]
        else:
            output, new_state = f(x, state)
            return ([output], new_state)

    h_agent(f_type, g, in_streams, [out_stream],
            state, call_streams, window_size, step_size)


def split(f_type, f, in_stream, num_outputs,
          state, call_streams, window_size, step_size):
    def g(x, state=None):
        if state is None: return f(x[0])
        else:
            #output, new_state = f(x[0], state)
            # return (output, new_state)
            return f(x[0], state)

    out_streams = h(f_type, g, [in_stream], num_outputs, state, call_streams,
                    window_size, step_size)
    return out_streams

def split_agent(f_type, f, in_stream, out_streams,
          state, call_streams, window_size, step_size):
    def g(x, state=None):
        if state is None: return f(x[0])
        else:
            # output, new_state = f(x[0], state)
            # return (output, new_state)
            return f(x[0], state)

    h_agent(f_type, g, [in_stream], out_streams,
            state, call_streams, window_size, step_size)


def op(f_type, f, in_stream, state, call_streams, window_size, step_size):
    def g(x, state=None):
        if state is None:
            return [f(x[0])]
        else:
            output, new_state = f(x[0], state)
            return ([output], new_state)

    out_streams = h(f_type, g, [in_stream], 1, state, call_streams,
                    window_size, step_size)
    return out_streams[0]

def op_agent(f_type, f, in_stream, out_stream,
             state, call_streams, window_size, step_size):
    def g(x, state=None):
        if state is None:
            return [f(x[0])]
        else:
            output, new_state = f(x[0], state)
            return ([output], new_state)

    h_agent(f_type, g, [in_stream], [out_stream],
            state, call_streams, window_size, step_size)


def single_output_source(f_type, f, num_outputs, state, call_streams,
                         window_size, step_size):

    def g(x, state=None):
        if state is None:
            return [f()]
        else:
            output, new_state = f(state)
            return ([output], new_state)

    out_streams = h(f_type, g, call_streams, num_outputs, state, call_streams,
                    window_size, step_size)
    return out_streams[0]

def single_output_source_agent(
        f_type, f, out_stream, state, call_streams,
        window_size, step_size):

    def g(x, state=None):
        if state is None: return [f()]
        else: return [f(state)]

    return h_agent(f_type, g, [], [out_stream],
            state, call_streams, window_size, step_size)



def many_outputs_source(f_type, f, num_outputs, state, call_streams,
                        window_size, step_size):
    def g(x, state=None):
        if state is None: return f()
        else:
            #output, new_state = f(state)
            return f(state)

    out_streams = h(f_type, g, call_streams, num_outputs, state, call_streams,
                    window_size, step_size)
    return out_streams


def sink(f_type, f, in_stream, state, call_streams, window_size, step_size):
    def g(x, state=None):
        if state is None: return f(x[0])
        else: return ([], f(x[0], state))

    ## out_streams = h(f_type, g, [in_stream], 0, state, call_streams,
    ##                 window_size, step_size)
    h(f_type, g, [in_stream], 0, state, call_streams, window_size, step_size)
    #return out_streams
    return None

def sink_merge(f_type, f, in_streams, state, call_streams, window_size, step_size):
    def g(x, state=None):
        if state is None: return f(x)
        else: return ([], f(x, state))

    ## out_streams = h(f_type, g, [in_stream], 0, state, call_streams,
    ##                 window_size, step_size)
    h(f_type, g, in_streams, 0, state, call_streams, window_size, step_size)
    #return out_streams
    return None

""" PART 3 OF MODULE.
A function, stream_func, that provides a single common signature for
converting operations on Python structures to operations on streams
regardless of whether the function has no inputs, a single input stream,
a list of input streams, or no outputs, a single output stream or a
list of output streams.
"""


def stream_func(inputs, f_type, f, num_outputs, state=None, call_streams=None,
                window_size=None, step_size=None):
    """ Provides a common signature for converting functions f on standard
    Python data structures to streams.

    Parameters
    ----------
    f_type : {'element', 'list', 'window', 'timed', 'asynch_element'}
       f_type identifies the type of function f where f is the next parameter.
    f : function
    inputs : {Stream, list of Streams}
       When stream_func has:
          no input streams, inputs is None
          a single input Stream, inputs is a single Stream
          multiple input Streams, inputs is a list of Streams.
    num_outputs : int
       A nonnegative integer which is the number of output streams of
       this function.
    state : object
       state is None or is an arbitrary object. The state captures
       all the information necessary to continue processing the input
       streams.
    call_streams : None or list of Stream
       If call_streams is None then the program sets it to inputs
       (converting inputs to a list of Stream if necessary).
       This function is called when, and only when any stream in
       call_streams is modified.
    window_size : None or int
       window_size must be a positive integer if f_type is 'window'
       or 'timed'. window_size is the size of the moving window on
       which the function operates.
    step_size : None or int
       step_size must be a positive integer if f_type is 'window'
       or 'timed'. step_size is the number of steps by which the
       moving window moves on each execution of the function.

    Returns
    -------
    list of Streams
       Function f is applied to the appropriate data structure in
       the input streams to put values in the output streams.
       stream_func returns the output streams.
    """

    # Check types of parameters
    if not isinstance(num_outputs, int):
        raise TypeError('Expected num_outputs to be int, not:',
                        num_outputs)
    if num_outputs < 0:
        raise ValueError('Expected num_outputs to be nonnegative, not:',
                         num_outputs)

    if not((inputs is None) or
           (isinstance(inputs, Stream) or isinstance(inputs, StreamArray) or
           ((isinstance(inputs, list) and
             (all((isinstance(l, Stream) or isinstance(inputs, StreamArray))
                    for l in inputs))
             )
           ))):
        raise TypeError('Expected inputs to be None, Stream or list of Streams, not:',
                        inputs)

    if not((call_streams is None) or
           ((isinstance(call_streams, list) and
             (all(isinstance(l, Stream) for l in call_streams))
             )
           )):
        raise TypeError('Expected call_streams to be None, Stream or list of Streams, not:',
                        call_streams)

    if inputs is None:
        # Check that call_streams is nonempty
        if len(call_streams) < 1:
            raise TypeError('Expected call_streams to be a nonempty list of streams, not:',
                        call_streams)

        if num_outputs == 0:
            raise TypeError('The function has no input or output streams.')

        elif num_outputs == 1:
            # No inputs. Single output stream.
            return single_output_source(f_type, f, num_outputs,
                                        state, call_streams,
                                        window_size, step_size)
        else:
            # No inputs. List of multiple output streams.
            return many_outputs_source(f_type, f, num_outputs,
                                       state, call_streams,
                                       window_size, step_size)

    elif isinstance(inputs, Stream) or isinstance(inputs, StreamArray):
        in_stream = inputs
        if num_outputs == 0:
            # Single input stream. No outputs.
            return sink(f_type, f, in_stream, state, call_streams,
                        window_size, step_size)
        elif num_outputs == 1:
            # Single input stream. Single output stream.
            return op(f_type, f, in_stream, state, call_streams, window_size, step_size)
        else:
            # Single input stream. List of multiple output streams.
            return split(f_type, f, in_stream, num_outputs, state, call_streams,
                         window_size, step_size)

    else:
        # Multiple input streams
        if num_outputs == 0:
            # sink
            return sink_merge(f_type, f, inputs, state, call_streams, window_size, step_size)
            #raise TypeError('A sink has exactly one input stream.')
        elif num_outputs == 1:
            # Multiple input streams, single output stream
            return merge(f_type, f, inputs, state, call_streams, window_size, step_size)
        else:
            # Multiple input and output streams
            return many_to_many(f_type, f, inputs, num_outputs, state, call_streams, window_size, step_size)



def stream_agent(inputs, outputs, f_type, f,
                 state=None, call_streams=None,
                window_size=None, step_size=None):
    """ Provides a common signature for converting functions f on standard
    Python data structures to streams.

    Parameters
    ----------
    f_type : {'element', 'list', 'window', 'timed', 'asynch_element'}
       f_type identifies the type of function f where f is the next parameter.
    f : function
    inputs : {Stream, list of Streams}
       When stream_func has:
          no input streams, inputs is None
          a single input Stream, inputs is a single Stream
          multiple input Streams, inputs is a list of Streams.
    outputs : list of Streams
    state : object
       state is None or is an arbitrary object. The state captures
       all the information necessary to continue processing the input
       streams.
    call_streams : None or list of Stream
       If call_streams is None then the program sets it to inputs
       (converting inputs to a list of Stream if necessary).
       This function is called when, and only when any stream in
       call_streams is modified.
    window_size : None or int
       window_size must be a positive integer if f_type is 'window'
       or 'timed'. window_size is the size of the moving window on
       which the function operates.
    step_size : None or int
       step_size must be a positive integer if f_type is 'window'
       or 'timed'. step_size is the number of steps by which the
       moving window moves on each execution of the function.

    Returns
    -------
    None
    """

    # Check types of parameters
    if not((outputs is None) or
           (isinstance(outputs, Stream) or
           ((isinstance(outputs, list) and
             (all(isinstance(l, Stream) for l in outputs))
             )
           ))):
        raise TypeError('Expected outputs to be None, Stream or list of Streams, not:',
                        inputs)

    if(isinstance(outputs, Stream)):
        num_outputs = 1
    elif(isinstance(outputs, list)):
        num_outputs = len(outputs)
    elif not outputs:
        num_outputs = 0

    if not((inputs is None) or
           (isinstance(inputs, Stream) or
           ((isinstance(inputs, list) and
             (all(isinstance(l, Stream) for l in inputs))
             )
           ))):
        raise TypeError('Expected inputs to be None, Stream or list of Streams, not:',
                        inputs)

    if not((call_streams is None) or
           ((isinstance(call_streams, list) and
             (all(isinstance(l, Stream) for l in call_streams))
             )
           )):
        raise TypeError('Expected call_streams to be None, Stream or list of Streams, not:',
                        call_streams)

    if inputs is None:
        # Check that call_streams is nonempty
        if len(call_streams) < 1:
            raise TypeError('Expected call_streams to be a nonempty list of streams, not:',
                        call_streams)

        if num_outputs == 0:
            raise TypeError('The function has no input or output streams.')

        elif num_outputs == 1:
            # No inputs. Single output stream.
            return single_output_source_agent(
                f_type, f, outputs, state, call_streams,
                window_size, step_size)
        else:
            # No inputs. List of multiple output streams.
            return many_outputs_source_agent(
                f_type, f, outputs, state, call_streams,
                window_size, step_size)

    elif isinstance(inputs, Stream) or isinstance(inputs, StreamArray):
        if num_outputs == 0:
            # Single input stream. No outputs.
            return sink(f_type, f, inputs, state, call_streams,
                        window_size, step_size)
        elif num_outputs == 1:
            # Single input stream. Single output stream.
            return op_agent(f_type, f, inputs, outputs,
                            state, call_streams, window_size, step_size)
        else:
            # Single input stream. List of multiple output streams.
            return split_agent(f_type, f, inputs, outputs,
                         state, call_streams, window_size, step_size)

    else:
        # Multiple input streams
        if num_outputs == 0:
            # sink
            return sink_agent()
        elif num_outputs == 1:
            # Multiple input streams, single output stream
            return merge_agent(f_type, f, inputs, outputs,
                         state, call_streams, window_size, step_size)
        else:
            # Multiple input and output streams
            return many_to_many_agent(f_type, f, inputs, outputs,
                                state, call_streams, window_size, step_size)


def main():
    def squares(l):
        return [v*v for v in l]
    def sums(v, state):
        return (v+state, v+state)

    def sums_asynch(v_and_i, state):
        v, i = v_and_i
        return (v+state, v+state)

    def max_min(v_and_i, state):
        max_so_far, min_so_far = state
        v, i = v_and_i
        max_so_far = max(max_so_far, v)
        min_so_far = min(min_so_far, v)
        state = (max_so_far, min_so_far)
        return([max_so_far, min_so_far], state)

    x_stream = Stream('x')
    w_stream = Stream('w')

    y_stream = stream_func(
        inputs=x_stream,
        f_type='element',
        f=sums,
        state=0.0,
        num_outputs=1)
    y_stream.set_name('cumulative sum of x')

    z_stream = stream_func(
        inputs=[x_stream, w_stream],
        f_type='asynch_element',
        f=sums_asynch,
        state=0.0,
        num_outputs=1)
    z_stream.set_name('asynch element. Cumulative sum of x and w')

    r_stream, s_stream = stream_func(
        inputs=[x_stream, w_stream],
        f_type='asynch_element',
        f=max_min,
        state=(0, 1000),
        num_outputs=2)
    r_stream.set_name('asynch element. max of x and w')
    s_stream.set_name('asynch element. min of x and w')

    x_stream.extend(range(5))
    w_stream.extend([100, -1, 10, 201, -31, 72])
    x_stream.print_recent()
    w_stream.print_recent()
    y_stream.print_recent()
    z_stream.print_recent()
    r_stream.print_recent()
    s_stream.print_recent()

if __name__ == '__main__':
    main()
